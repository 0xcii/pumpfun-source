# w12a05-cto-framemir: admin_cto frame layout via MIR (notes)

Target: `0x22a10` `admin_cto::execute` (`programs/pump/src/creator/admin_cto.rs`), pinned at 27,400 B.
Base: main `20a1ae9c0` (admin_cto 0.43919, 3,352 slots); main moved to `70f27048e` (0.45147, 3,308) during
the lane, and the frame findings below carry over (k4size changed code, not the frame anchors).
Builds and scratch: `~/.cache/pumpfun-reconstruction/lanes/w12a05-cto-framemir/` (not in git).
Ledger approach `frame-mir-*`, keys `0x22a10-w12-20a1ae9-framemir-*-v1`.

## Tools (this directory)

| tool | use |
| --- | --- |
| `tools/capmir.py <crate_copy> <work> <out>` | identity-recipe build of an experiment copy with `--emit=link,llvm-ir,mir`; copies `pump_recovered.{ll,mir}` to `<out>` (candidate.so equals a plain build) |
| `tools/framesim.py <fo_dir> [ops]` | frame what-if **with the ratio it would give**: re-lays-out the surviving frame objects of a `frameoracle.py` run (`mv:FI:BEFORE`, `sz:FI:SIZE[:AL]`, `ins:BEFORE:SIZE[:AL]`, `del:FI[:INTO]`), remaps every r10 access of our own code object-relative, prints the masked-exact ratio (= target_metric ratio on main) |
| `tools/r10.py orig\|<so> LO HI` | every instruction of the window touching `[r10-T]`, LO<=T<=HI (incl. `mov rX,r10; add rX,-T`) |
| `tools/nosc_rows.py <fo_dir>` | per-alloca implied original T from frameoracle's `-no-stack-coloring` run (all rows, not just confident ones) |
| `tools/dis.py <so>` | disassembly of a candidate's `admin_cto::execute` |

## The 56-byte first-spill gap is two things

The original spills its args at `[r10-0x928]` (r4), ours at `[r10-0x8f0]`. That is not one local:

- **+32 B in the alloca region**: mint/holder_key are at T 0x6c0/0x6a0 in the original, 0x6a0/0x680 in ours,
  and the 33 call-return slots follow at +32.
- **+24 B in the spill area**: the four arg spill slots are in a different order (orig r1/r3/r4/r2 at
  0x8f0/0x918/0x928/0x938, ours 0x8c8/0x8b8/0x8f0/0x8f8). Spill slots are created by the register
  allocator, so this part follows from code shape, not from any local.

## Alloca region, original vs main 20a1ae9 (T = r10 displacement of the object base)

Read from the original's code with `r10.py` and from frameoracle's aligned accesses:

| orig T | size | what the original keeps there (from its code) | ours |
| --- | ---: | --- | --- |
| 0x470 | 32 | wallet emit_cpi seeds `[&[u8];2]` (`_120.i`) | same, 0x470 |
| — | 16 | — | **`_117.i74` wallet emit_cpi signer slice `[&[&[u8]];1]`, standalone at 0x480** |
| 0x488..0x530 | | `_110.i`, `_94.i`, `ix_data.i`, `inner_data.i`, `authority_info.i`, `val.sroa.6.i` groups | same groups at +16 (0x498..0x540) |
| 0x538 | 7 | Option-layout `[1,8)` piece P1a: written in both validate arms (new's piece in the non-holder arm), read at the validate exit | none |
| 0x548 | 9 | P1b `[24,33)` piece; later hosts the wallet emit_cpi bump (`stxb [r10-0x548]` at 0x29148) | none (bump `_124.i` is hosted by `target.sroa.0`) |
| 0x550 / 0x560 | 7 / 9 | P2 = copy of P1 made at the validate exit (0x243e0..0x24418); read to build the sharing CPI `val` (0x26738) | none |
| 0x580 | 32 | full `target`: `[0,8)` from a spilled i64 (`[r10-0x918]`), `[8,32)` from X24; read for `curve.creator=` (0x27518) and passed as `&target` to admin_cto_pool (0x27820) | `target1` = MIR `_55`, 32 B, **no lifetime markers**, at 0x658 |
| 0x598..0x630 | | `_184`, `_169`, `inner_data`, `authority_info`, `old_creator` | same, at -64 (0x558..0x5f0) |
| 0x651 | 33 | `val` (sharing CPI Option<Pubkey>) | `val7`, 0x611 |
| 0x658 / 0x668 | 7 / 9 | copy of `new` made at entry (0x22f00..0x22f48), read once in the non-holder arm into P1 | none |
| — | 32 + 32 | — | **`sharing_update2.sroa.3` = MIR `_56` (32 B) and `target1` = `_55` (32 B), both without StorageLive/Dead**, plus `target.sroa.0` (7 B) |
| 0x680 | 24 | X24 = `target[8..32)` at the validate exit (0x243b8..0x24450); later **hosts the wallet signer slice** (0x29108/0x29150/0x29170) | none |
| 0x6a0 / 0x6c0 | 32 / 32 | holder_key / mint | 0x680 / 0x6a0 |

Net: -16 (signer slice) +80 (P1, P2, target before `_184`) -32 (between old_creator and holder_key) = +32.

MIR facts behind the "ours" column (main 20a1ae9, `--emit=mir`):
- `_55` (outer `target`) and `_56` (outer `sharing_update`) have no `StorageLive`/`StorageDead` at all: the
  tuple destructuring `let (holder,cashback,target,sharing_update,collect_old)={..}` is copy-propagated, and
  `let mut target=target;` is the same local. Without lifetime markers StackColoring never merges them.
- The block-internal `target` (`_36`) is split 7/16/9 (`target.sroa.0`, two i64, `target.sroa.8`) because it is
  copied out of `ControlFlow<.., Pubkey>`/`Result<Pubkey>` whose `Error` overlaps bytes `[8,24)` (Pubkey at
  offset 1).
- The original's `target` copies are split 8/24 instead (`[0,8)` in a register, `[8,32)` in memory: X24 and the
  `[r10-0x530]` piece), so its execute-level target is not a plain copy of a `Result<Pubkey>` payload.

## What-if bounds (`framesim.py`, our own code remapped, no build)

| what-if on main 20a1ae9 | ratio |
| --- | ---: |
| none | 0.43919 |
| signer slice moved into a 24 B slot just above holder_key (`sz:41:24 mv:41:144`) | 0.45506 |
| full original alloca order through mint (P1/P2/target before `_184`, new-copy 7/9 + X24 before holder_key) | 0.49371 |
| every r10 offset remapped to its aligned original offset (incl. spills; `w3-adminCTO/scripts/remap.py`) | 0.5707 |

(w12b12-cto-cpi's IR oracle moves `_117.i74` without growing it and gets 0.48892 for that alone.)

## Which Rust shapes give the original's 8/24 target split

Measured on the pinned rustc 1.79 (host target, same layout code; `tools/layout_probe.rs`, run with `RUSTC_BOOTSTRAP=1 ~/.cache/solana/v1.44/platform-tools/rust/bin/rustc -O tools/layout_probe.rs`): offset of
the Pubkey and of the `Error` inside `Result<T, anchor Error>`.

| `T` | Pubkey at | Error at | Pubkey bytes overlapped |
| --- | ---: | --- | --- |
| `Pubkey` (main) | 1 | [8,24) | [7,23): 7/16/9 split, as on main |
| `(Pubkey,Option<u64>)` | 0 | [0,16) | [0,16): 16/16 split (trial h3a) |
| `(Option<u64>,Pubkey)`, `(Pubkey,Option<u64>,bool)` | 16 | [8,24) | **[0,8): 8/24 split, as in the original** |
| `(bool,bool,Pubkey,Option<u64>,Option<Option<Pubkey>>,bool)` (block tuple plus fee) | 16 | [8,24) | **[0,8)** |
| `(bool,bool,Pubkey,Option<Option<Pubkey>>,bool)` (main's block tuple) | 36 | [8,24) | none |
| `(Pubkey,u64)`, `(u64,Pubkey,bool)`, `(Pubkey,usize)` | 8 or 0 | | [0,16) |

So the original's target most likely travels through a `Result`/`ControlFlow` whose Ok payload is 8-aligned
with the Pubkey at payload offset 16 (an `Option<u64>` such as `fee` placed first), e.g. a validation closure or
helper returning the block tuple plus `fee` with `?`.

## Trials (main 20a1ae9, `capmir.py` builds; target_metric on the unstripped output)

| trial | change | bytes | ratio | frame result |
| --- | --- | ---: | ---: | --- |
| va1 | deferred-init outer locals `let (holder,cashback,mut target,sharing_update,collect_old);{..}` | 27,368 | 0.26589 | outer target becomes 7/9 pieces (like the orig's 0x658/0x668 pair) but still without lifetime markers; `target.sroa.0` disappears, so the wallet bump `_124.i` becomes a standalone 1 B slot and the whole top of the frame moves by -8 (r10-equal 670 -> 37) |
| h3a/h3b | `validate` returns `Result<(Pubkey,Option<u64>)>` (fee carried out / ignored; identical bytes) | 27,760 | 0.19908 | 16/16 split (Pubkey at offset 0, see table) |
| h4a | validation block as an immediately called closure returning `Result<(bool,bool,Pubkey,Option<u64>,Option<Option<Pubkey>>,bool)>` with `?` | 27,808 | 0.37877 | the outer `target` (32 B) and outer `sharing_update` 7/9 pieces move **in front of `_184`** (frame-index order of the original's target/P2), the closure's `sharing_update` 7 B piece aligns with orig P1a (0x538, 2/2 votes), the closure result `_26` 7/9 pieces align with orig P2 (0x550/0x560, 2/2), `target` with orig 0x580 (5/6), and the wallet bump is hosted by the closure's 9 B target piece like orig P1b; abstracted ratio 0.6465 -> 0.5809 (+408 B of code) |

h4a is the first shape that reproduces the original's frame-index order for the target/sharing pieces; it is
too large and changes too much code to land. The signer slice is still standalone in h4a (no 24 B X24).

## Next ideas

- h4a-style shape with the 8/24 split reaching the execute-level target (X24): the Pubkey must come out of a
  payload where it sits at offset 16 behind an `Option<u64>`; then StackColoring gets the 24 B partner for
  `_117.i74` by itself.
- Keep main's code and only replace `let mut target=validate(..)?` by a helper returning `Result<(Option<u64>,Pubkey)>`
  (fee first) to test the split in isolation.
- Combine with the new main (70f27048e) genes and size knobs (`w12a13-cto-sizeknobs`) to get back to 27,400 B.
