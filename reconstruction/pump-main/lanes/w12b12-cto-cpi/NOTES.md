# Lane w12b12-cto-cpi (wave 12, pool b): CPI construction forms in `admin_cto::execute`

Target: `0x22a10` `admin_cto::execute` (`programs/pump/src/creator/admin_cto.rs`), pinned at 27,400 B.
Base: main 20a1ae9c0 (`$BASE` sha 8cd7695c…): 1033/1033 normalized/raw, admin_cto 0.43919, 3,352 slots.
Builds and scratch: `~/.cache/pumpfun-reconstruction/lanes/w12b12-cto-cpi/` (not in git).
Ledger approach `cpi-forms`, keys `0x22a10-w12-20a1ae9-cpi-<variant>-v1`.

## Oracle: the wallet `emit_cpi!` signer-seeds array is worth +0.050

The frame oracle (`w4-frame-oracle/frameoracle.py`, llc on main's own IR, no build slot) shows one
16-byte alloca that shifts the middle of the frame: `%_117.i74`, the `&[&[b"__event_authority",&[bump]]]`
array that anchor's `emit_cpi!` builds for `invoke_signed` inside the inlined `wallet` (the
`CollectCreatorFeeEvent` emission). In ours it is its own StackColoring slot at frame index 41
(T=0x480), in front of the wallet's `_110.i`, `_94.i`, `ix_data.i`, `inner_data.i`,
`authority_info.i` and `val.sroa.6.i` slots. Those all sit 16 bytes too deep (delta -16), and so do
the pool-authority signer seeds that share their slots (`_100`, `_93`, `pb`).

| IR what-if (`--move-alloca`, main IR) | masked-exact ratio |
| --- | ---: |
| none (main) | 0.43919 |
| `_117.i74` moved anywhere after `val.sroa.6.i` (before `_60.i`, `_184`, `_67`, `val7`, `st`, `_8`, `holder_key`, or END) | **0.48892** |
| `_117.i74` moved only one slot later (before `_110.i`) | 0.43919 |
| plus `target1`, `target.sroa.0/8`, `sharing_update2.sroa.3` moved before `_184` | 0.48892 (no further gain: still 8 B off) |

So the gain needs only that the 16 bytes leave the run fi41–fi53: either the array merges into some other
slot, or its alloca comes after `val.sroa.6.i`. With it gone, fi40–fi53 all line up with the original
(delta 0). The next frame break is +80 B between `val.sroa.6.i` and `_184`.

Where the original keeps it: at `[r10-0x680]` (`0x29108 stxdw [r10-0x680]`, `0x29150 stdw [r10-0x678],0x2`,
`0x29170 add64 r1,-0x680`). The same 24 bytes `[r10-0x680..-0x668)` hold `target[8..32)` earlier, at
`0x243b0..0x24458`, just before `prepare_bonding_curve`. So the original's StackColoring merged the
emit seeds into a 24-byte, short-lived, execute-local `target` piece placed next to `holder_key`
(T=0x6a0). Ours has no such slot. Our `target` is split 7/16/9 (`target.sroa.0` 7 B, two i64 in
registers, `target.sroa.8` 9 B). That split comes from the offset-1 Pubkey inside
`Result<Pubkey>`/`ControlFlow` (validate's `?`). The original splits every target copy 8/24: `[0..8)` in a
register (spill `[r10-0x918]`) and `[8..32)` in memory (`[r10-0x530]` → `[r10-0x680]` → `[r10-0x578]`). A
source shape that makes the execute-local `target` an 8/24 split should give StackColoring a 24-byte
partner for the emit seeds, and that should be worth about +0.05.

The original's pool-CPI `target` argument (`r3 = r10-0x580`) is a 32-byte slot early in frame order,
just ahead of the final `emit_cpi!` temporaries (`_184` at T=0x598). It is preceded by two 7/9-byte pairs at
T=0x538/0x548 and 0x550/0x560 (copies made at 0x243e0..0x24418). Ours keeps `target1` (32 B, no lifetime
markers) near `holder_key`. These objects make up the +80/-48 B breaks that remain after the fix above.

## CPI shapes compared with the original

- The call boundaries of all CPIs match the original: 4 `declare_program!` CPIs, 2 `create_idempotent`,
  `collect`, `transfer_vault_tokens`, `transfer_native`, 2 inlined `emit_cpi!`.
- CpiContext/accounts slots match: pool `_130` at T=0x2d0, accounts `_132` memcpy source at T=0x450,
  sharing `_105` at T=0x2d0. The `signer_seeds` slice is at 0x4e0 in ours and 0x4d0 in the original, which
  is the -16 shift described above.
- `holder` reaches the pool CPI as `and64 rX,0xff; jne` (an i1 rebuilt from `(holder_opt & -3) != 0`) in
  ours. The original reloads a canonical 0/1 spill `[r10-0x950]`, a phi of constants set in the validate
  arms (`0x23b38 mov64 r1,1; stxdw [r10-0x950],r1`).

## Trials (measure.sh, main 20a1ae9)

| variant | change | bytes | ratio | losses |
| --- | --- | ---: | ---: | --- |
| sws | sharing CPI `CpiContext::new(..).with_signer(seeds)` | 27,424 | 0.40844 | size |
| pws | pool CPI `.with_signer(seeds)` | 27,400 | 0.37328 | 0/0 |
| seedsinline | both signed CPIs take `&[&[b"pool-authority",mint.as_ref(),&[bump]]]` inline | 27,584 | 0.39982 | size |
| pocurveargs | pool CPI args read back from the curve account | 27,368 | 0.26589 | size |
| shclos | sharing CPI as a migrate.rs-style `move \|signer_seeds:&[&[&[u8]];1]\|` closure | 27,432 | 0.40808 | size |
| shclosinl | the same closure, called with inline seeds | 27,520 | 0.40741 | size |
| poclos | pool CPI as a migrate.rs-style closure, called as `cto(&[poolseeds])?` | 27,080 | 0.25980 | size |
| poclosinl | the pool closure, called with inline seeds | 27,200 | 0.28391 | size |
| poacclet | pool CPI accounts struct bound with `let` before `new_with_signer` | 27,400 | 0.37148 | 0/0 |
| shacclet | sharing CPI accounts struct bound with `let` | 27,368 | 0.41876 | size |
| walletinline | `wallet` body written inline in `execute` (emit seeds become execute MIR locals) | 28,920 | 0.09926 | 1 normalized |
| walletinlalways | `#[inline(always)] fn wallet` (MIR-inlined) | 27,184 | 0.36481 | size |
| tgtout | validate writes target through `&mut Pubkey`, returns `Result<()>` | 27,264 | 0.28202 | size |
| tgtunit | validate returns `Result<()>`; target computed in execute | 27,024 | 0.13909 | size |

The same oracle was found independently by w12a02-cto-iroracle (#2772) and w12a12-cto-ctxuse (#2786). Both
have the full slot map of the original from T 0x530 to 0x6c0. ctxuse also measured the pad and merge variants.

## Round 2 (main b5975fa / 70f2704): admin_cto 0.45147, 3,308 slots, 27,400 B

### Gain: pool-authority signer seeds as one nested literal (+0.0009 at 27,400 B, 0 losses)

```rust
// before
let pb=[ctx.bumps.pool_authority];let poolseeds:&[&[u8]]=&[b"pool-authority",mint.as_ref(),&pb];let signer_seeds:&[&[&[u8]]]=&[poolseeds];
// after
let signer_seeds:&[&[&[u8]]]=&[&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]]];
```

| metric | main 70f2704 | this change |
| --- | ---: | ---: |
| admin_cto ratio | 0.45147 | **0.45237** |
| admin_cto slots_diff | 3,308 | 3,308 |
| admin_cto bytes | 27,400 | 27,400 |
| normalized / raw | 1034 / 1034 | 1034 / 1034 |
| losses / raw losses | | 0 / 0 |
| admin_cto runtime differential | | 363 cases, 0 mismatches |
| unstripped sha256 | | 9a06045fc5ac1ac7… |

Mechanism: the seed stores before the sharing CPI now follow the original's order (`0x26680..0x26708` in the
original). The bump load comes first, then the `&bump`, `&mint` and `"pool-authority"` pointer stores, then the bump byte
store, then the signer-slice pointer, and last the lengths 1, 0x20, 0xe and 3. With separate `pb`/`poolseeds` locals,
the bump byte was stored first and the signer slice after the lengths. Only the -16 B slot shift from
the emit signer slice remains in this block. w10r1-admincto-cpi measured the same form (v2) on e61baa9
(+0.0009, same size) but never landed it.

PR #2776 (notes) was merged. This round continues on `swarm/w12b12-cto-cpi-2`.

### StackColoring trace tool: `tools/scmerge.py` (about 5 s, no build slot)

`scmerge.py --ll module.ll --sym admin_cto7execute [--edit e.py] --slot NAME` extracts the function with
the debug build's `llvm-extract` and runs the debug `llc` with `-debug-only=stack-coloring`. It prints every
StackColoring group (representative, size, members) and where each `--slot` ended up. The extracted
module compiles to the same bytes as the full module (27,400 B, identical disassembly).

What it shows for the emit signer slice `%_117.i74` (#41) on main 20a1ae9 IR:
- Every StackColoring group of 16 B or more has exactly one member that is live at the slice's start.
  That member is a sibling from the same `emit_cpi!`/event: `ix.i` (#22), `e.i` (#37), `_114.i` (#15),
  `_94.i` (#46), `authority_info.i` (#49), `_120.i` (#40), `_110.i` (#43), `ix_data.i` (#47),
  `inner_data.i` (#48), `val.sroa.6.i` (#54). The other two groups are `holder_key` and `mint`, which
  live across the wallet. So the slice has no host and becomes its own representative at fi41. It
  then absorbs validate's 7 B `target.i.sroa.0`.
- Growing the target pieces to 24 B, as in the original's 8/24 split, fills the existing 24 B groups but adds no
  new host. validate's tail goes to `ix_data.i` (#47), the `?` ControlFlow tail `_37.sroa.11` to
  `inner_data.i` (#48), and execute's `target.sroa.8` to `val.sroa.6.i` (#54). All three are absorbed
  before the 16 B slice is considered (size order), so the slice stays at fi41 (ratio unchanged).
- The original has one more 24 B tail copy, at T 0x680. It is written at the validation join and read just
  before `prepare_bonding_curve`. That fourth piece, live while the other three are, becomes its own
  representative and hosts the slice. An IR emulation (`tools/ired/x6.py`: a fourth 24 B `t24` between
  `target.sroa.8` and `target1`) did not reproduce it. The copy through `t24` was store-forwarded away in the DAG,
  which left an EMPTY interval. The original's T24 survives codegen, so its accesses are not
  forwardable within one block.

### CPI-form trials on main b5975fa

| variant | change | bytes | ratio | losses |
| --- | --- | ---: | ---: | --- |
| m2_shvalt | sharing CPI `val` built from the validated target (`Some(Some(t))`, t = target before the `st.creator` override) instead of `Some(new)` | 27,568 | 0.42736 | size |
| m2_shvalt2 | the same, as `let su=(Some(Some(target)),false);` | byte-identical to m2_shvalt | | |
| m2_seedsnested / m3_seedsnested | nested signer-seed literal (above) | 27,400 | **0.45237** | 0 / 0 |
