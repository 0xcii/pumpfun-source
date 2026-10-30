# Size/ratio knobs over the k4 admin_cto.rs (w9r2-admincto-harvest k4 ported onto main 20a1ae9).
# Each gene is a list of (old, new) substitutions; every substitution keeps the newline count, so
# every require!/error! site keeps its line (line!() immediates are code).
SHARED = "let shared=a.bonding_curve.creator==a.sharing_config.key()&&a.sharing_config.owner==&FEES&&!a.sharing_config.data_is_empty();"
QL = "let quote_locked=crate::pump_quote::global_quote(a.bonding_curve.quote_mint,&a.global);"
HK = "let (holder_key,_)=Pubkey::find_program_address(&[b\"holder-rewards\",mint.as_ref()],&crate::ID);"
HOLDER = "let holder=holder==Some(true);"
CB = "let cashback=!holder&&st.cashback;"
VAL = "let mut target=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;"
R2 = "let (sharing_update,collect_old)=if shared{if holder{(Some(None),false)}else{target=st.creator;(Some(new),false)}}else{(None,!st.holder_reward&&st.creator!=Pubkey::default())};"
R2_OLD = "let sharing_update=if shared{Some(if holder{None}else{new})}else{None};let collect_old=!shared&&!st.holder_reward&&st.creator!=Pubkey::default();if shared&&!holder{target=st.creator;}"
TUP = "(holder,cashback,target,sharing_update,collect_old)};let mut target=target; "
PREP = "crate::trade_types::prepare_bonding_curve(&a.bonding_curve,&a.system_program,&a.admin_set_creator_authority)?;"
OLDBUMP = "let old=a.current_creator.key();let bump=[ctx.bumps.creator_vault];"
AMT = "let amount=token_raw_amount(a.creator_vault_quote_token_account.as_ref())?;"
FRZ = "let frozen=token_frozen(a.creator_vault_quote_token_account.as_ref())?;"
NATIVE = "let native=a.quote_mint.key()==anchor_spl::token::spl_token::native_mint::ID;"
POOL = "let pool_updated=a.pool.owner==&AMM && !a.pool.data_is_empty();"
CURVE0 = "let curve=&mut ctx.accounts.bonding_curve;let old_fee=curve.creator_fee_bps;let old_creator=curve.creator;curve.can_edit_creator_fee=false;"

G = {
    # ---- execute prologue ----
    'ql_first': [(SHARED + QL, QL + SHARED)],
    'hk_after_shared': [(HK + SHARED, SHARED + HK)],
    'shared_owner_first': [(SHARED, "let shared=a.sharing_config.owner==&FEES&&a.bonding_curve.creator==a.sharing_config.key()&&!a.sharing_config.data_is_empty();")],
    'shared_empty_first': [(SHARED, "let shared=!a.sharing_config.data_is_empty()&&a.bonding_curve.creator==a.sharing_config.key()&&a.sharing_config.owner==&FEES;")],
    'shared_key_lhs': [(SHARED, "let shared=a.sharing_config.key()==a.bonding_curve.creator&&a.sharing_config.owner==&FEES&&!a.sharing_config.data_is_empty();")],
    'shared_bitand': [(SHARED, "let shared=(a.bonding_curve.creator==a.sharing_config.key())&(a.sharing_config.owner==&FEES)&!a.sharing_config.data_is_empty();")],
    'ql_inline': [(QL, ""), ("quote_locked,holder_enabled", "quote_locked:crate::pump_quote::global_quote(a.bonding_curve.quote_mint,&a.global),holder_enabled")],
    'a_deref': [("->Result<()>{ let a=&ctx.accounts;let mint=a.mint.key();", "->Result<()>{ let a=&*ctx.accounts;let mint=a.mint.key();")],
    'holder_unwrap_or': [(HOLDER, "let holder=holder.unwrap_or(false);")],
    'holder_matches': [(HOLDER, "let holder=matches!(holder,Some(true));")],
    'holder_some_and': [(HOLDER, "let holder=holder.is_some_and(|h|h);")],
    'holder_before_st': [(HOLDER, ""), ("let (holder,cashback,target,sharing_update,collect_old)={let st=", HOLDER + "let (holder,cashback,target,sharing_update,collect_old)={let st=")],
    'cb_bitand': [(CB, "let cashback=!holder&st.cashback;")],
    'cb_after_val': [(CB + VAL, VAL + CB)],
    'cb_end': [(CB, ""), (R2 + "(holder,", R2 + CB + "(holder,")],
    'r2_revert': [(R2, R2_OLD)],
    'r2_match': [(R2, "let (sharing_update,collect_old)=match (shared,holder){(true,true)=>(Some(None),false),(true,false)=>{target=st.creator;(Some(new),false)}(false,_)=>(None,!st.holder_reward&&st.creator!=Pubkey::default())};")],
    'r2_co_rev': [("(None,!st.holder_reward&&st.creator!=Pubkey::default())", "(None,st.creator!=Pubkey::default()&&!st.holder_reward)")],
    'r2_holder_neg': [("if holder{(Some(None),false)}else{target=st.creator;(Some(new),false)}", "if !holder{target=st.creator;(Some(new),false)}else{(Some(None),false)}")],
    'r2_shared_neg': [("=if shared{if holder{(Some(None),false)}else{target=st.creator;(Some(new),false)}}else{(None,!st.holder_reward&&st.creator!=Pubkey::default())};",
                       "=if !shared{(None,!st.holder_reward&&st.creator!=Pubkey::default())}else if holder{(Some(None),false)}else{target=st.creator;(Some(new),false)};")],
    'target_rebind_drop': [(TUP, "(holder,cashback,target,sharing_update,collect_old)}; ")],
    'target_rebind_plain': [(TUP, "(holder,cashback,target,sharing_update,collect_old)};let target=target; ")],
    # ---- validate ----
    'v_or_order': [("if t==*holder_key||t==*sharing{", "if t==*sharing||t==*holder_key{")],
    'v_zero_rev': [("if t==Pubkey::default(){", "if Pubkey::default()==t{")],
    'v_fee_rev': [("if f==0||f>st.max_fee{", "if f>st.max_fee||f==0{")],
    'v_fee_contains': [("if f==0||f>st.max_fee{", "if !(1..=st.max_fee).contains(&f){")],
    'v_cb_rev': [("if !holder&&st.cashback{", "if st.cashback&&!holder{")],
    'v_hr_rev': [("if st.holder_reward&&!holder{", "if !holder&&st.holder_reward{")],
    'v_296_rev': [("if holder&&!st.holder_reward&&!st.holder_enabled{", "if holder&&!st.holder_enabled&&!st.holder_reward{")],
    'v_298_iflet': [("if new.is_some(){", "if let Some(_)=new{")],
    'v_keys_val': [("holder_key:&Pubkey,sharing:&Pubkey)->Result<Pubkey>{", "holder_key:Pubkey,sharing:Pubkey)->Result<Pubkey>{"),
                   ("*holder_key}else{", "holder_key}else{"), ("if t==*holder_key||t==*sharing{", "if t==holder_key||t==sharing{"),
                   ("new,&holder_key,&a.sharing_config.key())?", "new,holder_key,a.sharing_config.key())?")],
    'v_sharing_val': [("holder_key:&Pubkey,sharing:&Pubkey)->Result<Pubkey>{", "holder_key:&Pubkey,sharing:Pubkey)->Result<Pubkey>{"),
                      ("if t==*holder_key||t==*sharing{", "if t==*holder_key||t==sharing{"),
                      ("new,&holder_key,&a.sharing_config.key())?", "new,&holder_key,a.sharing_config.key())?")],
    # ---- wallet ----
    'w_flag': [(" if collect_old{wallet(&ctx)?;}fn wallet(ctx:&Context<AdminCto>)->Result<()>{let a=&ctx.accounts;",
                " wallet(&ctx,collect_old)?;fn wallet(ctx:&Context<AdminCto>,go:bool)->Result<()>{if !go{return Ok(());}let a=&ctx.accounts;")],
    'w_deref': [("fn wallet(ctx:&Context<AdminCto>)->Result<()>{let a=&ctx.accounts;", "fn wallet(ctx:&Context<AdminCto>)->Result<()>{let a=&*ctx.accounts;")],
    'w_dc_neg': [("let do_collect=collection_native||(!a.creator_vault_quote_token_account.data_is_empty()&&!token_frozen(a.creator_vault_quote_token_account.as_ref())?);",
                  "let do_collect=collection_native||!(a.creator_vault_quote_token_account.data_is_empty()||token_frozen(a.creator_vault_quote_token_account.as_ref())?);")],
    'w_dcoin_neg': [("let do_coin=coin_present&&!token_frozen(a.coin_creator_vault_ata.as_ref())?;", "let do_coin=!(!coin_present||token_frozen(a.coin_creator_vault_ata.as_ref())?);")],
    'w_cp_inline': [("  let coin_present=!a.coin_creator_vault_ata.data_is_empty();\n", "\n"),
                    ("let do_coin=coin_present&&", "let coin_present=!a.coin_creator_vault_ata.data_is_empty();let do_coin=coin_present&&")],
    'w_ata_rev': [("if !collection_native||coin_present{", "if coin_present||!collection_native{")],
    # ---- sweep ----
    'gate_rev': [("swept=(shared&&holder).then(", "swept=(holder&&shared).then(")],
    'gate_unwrap_def': [(".transpose()?.unwrap_or(0);fn sweep", ".transpose()?.unwrap_or_default();fn sweep")],
    's_bump_first': [(OLDBUMP, "let bump=[ctx.bumps.creator_vault];let old=a.current_creator.key();")],
    's_frozen_first': [(AMT + FRZ, FRZ + AMT)],
    's_native_late': [("->Result<u64>{let a=&ctx.accounts;" + NATIVE, "->Result<u64>{let a=&ctx.accounts;"), (OLDBUMP, NATIVE + OLDBUMP)],
    's_coin_present': [("let amm_frozen=!a.coin_creator_vault_ata.data_is_empty()&&token_frozen(", "let coin_present=!a.coin_creator_vault_ata.data_is_empty();let amm_frozen=coin_present&&token_frozen("),
                       ("else if !a.coin_creator_vault_ata.data_is_empty(){crate::pump_amm", "else if coin_present{crate::pump_amm")],
    's_dest_rev': [("if a.holder_creator_vault.key()!=dest{", "if dest!=a.holder_creator_vault.key(){")],
    's_amt_ne': [("   if amount>0{crate::legacy_buy", "   if amount!=0{crate::legacy_buy")],
    's_tok_amt_ne': [("else if amount>0{anchor_spl", "else if amount!=0{anchor_spl")],
    's_hk_val': [("swept=(shared&&holder).then(||sweep(&ctx,&holder_key))", "swept=(shared&&holder).then(||sweep(&ctx,holder_key))"),
                 ("fn sweep(ctx:&Context<AdminCto>,holder_key:&Pubkey)->Result<u64>{", "fn sweep(ctx:&Context<AdminCto>,holder_key:Pubkey)->Result<u64>{")],
    's_deref': [("->Result<u64>{let a=&ctx.accounts;", "->Result<u64>{let a=&*ctx.accounts;")],
    's_native_ok0': [("}else{Ok(amount)}}else{let amount", "}else{Ok(0)}}else{let amount")],
    's_checked_sub': [("a.creator_vault.lamports().saturating_sub(min);", "a.creator_vault.lamports().checked_sub(min).unwrap_or(0);")],
    's_lamports_first': [("let min=Rent::get()?.minimum_balance(0);let amount=a.creator_vault.lamports().saturating_sub(min);",
                          "let lamports=a.creator_vault.lamports();let amount=lamports.saturating_sub(Rent::get()?.minimum_balance(0));")],
    's_seeds_inline': [("let vaultseeds:&[&[u8]]=&[b\"creator-vault\",old.as_ref(),&bump];", "let vaultseeds=&[b\"creator-vault\".as_ref(),old.as_ref(),&bump];")],
    # ---- post-sweep ----
    'p_with_signer': [("admin_cto_sharing_config(CpiContext::new_with_signer(", "admin_cto_sharing_config(CpiContext::new("),
                      ("program:a.pump_fees.to_account_info()},signer_seeds),val)?;", "program:a.pump_fees.to_account_info()}).with_signer(signer_seeds),val)?;")],
    'p_amm_with_signer': [("admin_cto_pool(CpiContext::new_with_signer(", "admin_cto_pool(CpiContext::new("),
                          ("program:a.pump_amm.to_account_info()},signer_seeds),target,holder,fee)?;", "program:a.pump_amm.to_account_info()}).with_signer(signer_seeds),target,holder,fee)?;")],
    'p_su_match': [(" if let Some(val)=sharing_update{", " match sharing_update{Some(val)=>{"), (" }\n let (old_creator,old_fee)={", " }None=>{}}\n let (old_creator,old_fee)={")],
    'p_pool_rev': [(POOL, "let pool_updated=!a.pool.data_is_empty() && a.pool.owner==&AMM;")],
    'p_pool_key_eq': [(POOL, "let pool_updated=*a.pool.owner==AMM && !a.pool.data_is_empty();")],
    'p_hr_before_creator': [("  curve.creator=target;\n  curve.is_holder_reward=holder;", "  curve.is_holder_reward=holder;\n  curve.creator=target;")],
    'p_cb_before_hr': [("  curve.is_holder_reward=holder;\n  curve.is_cashback_coin=cashback;", "  curve.is_cashback_coin=cashback;\n  curve.is_holder_reward=holder;")],
    'p_canedit_revert': [(CURVE0, "let curve=&mut ctx.accounts.bonding_curve;let old_fee=curve.creator_fee_bps;let old_creator=curve.creator;"),
                         ("  curve.creator_fee_bps=fee.unwrap_or(old_fee);\n\n", "  curve.creator_fee_bps=fee.unwrap_or(old_fee);\n  curve.can_edit_creator_fee=false;\n")],
    'p_canedit_after_creator': [(CURVE0, "let curve=&mut ctx.accounts.bonding_curve;let old_fee=curve.creator_fee_bps;let old_creator=curve.creator;"),
                                ("  curve.creator=target;\n", "  curve.creator=target;curve.can_edit_creator_fee=false;\n")],
    'p_feeunwrap_revert': [("  curve.creator_fee_bps=fee.unwrap_or(old_fee);", "  if let Some(f)=fee{curve.creator_fee_bps=f;}")],
    'p_oldfee_revert': [("let old_fee=curve.creator_fee_bps;let old_creator=curve.creator;", "let old_creator=curve.creator;let old_fee=curve.creator_fee_bps;")],
    'p_canedit_first': [(CURVE0, "let curve=&mut ctx.accounts.bonding_curve;curve.can_edit_creator_fee=false;let old_fee=curve.creator_fee_bps;let old_creator=curve.creator;")],
    'p_ev_new_creator_local': [("new_creator:a.bonding_curve.creator,", "new_creator:target,")],
    'p_ev_flags_local': [("is_holder_reward:a.bonding_curve.is_holder_reward,is_cashback_coin:a.bonding_curve.is_cashback_coin,", "is_holder_reward:holder,is_cashback_coin:cashback,")],
    'p_ev_fee_local': [("new_creator_fee_bps:a.bonding_curve.creator_fee_bps,", "new_creator_fee_bps:fee.unwrap_or(old_fee),")],
    'p_ev_su_early': [(" let pb=[ctx.bumps.pool_authority];", " let reset=sharing_update.is_some();let pb=[ctx.bumps.pool_authority];"), ("sharing_config_reset:sharing_update.is_some(),", "sharing_config_reset:reset,")],
    'p_ev_clock_first': [(" let e=AdminCtoEvent{timestamp:Clock::get()?.unix_timestamp,", " let ts=Clock::get()?.unix_timestamp;let e=AdminCtoEvent{timestamp:ts,")],
    'p_a_reborrow': [(" let a=&ctx.accounts;\n let pool_updated", " let a=&*ctx.accounts;\n let pool_updated")],
    'p_seeds_inline': [(" let pb=[ctx.bumps.pool_authority];let poolseeds:&[&[u8]]=&[b\"pool-authority\",mint.as_ref(),&pb];let signer_seeds:&[&[&[u8]]]=&[poolseeds];",
                        " let pb=[ctx.bumps.pool_authority];let signer_seeds:&[&[&[u8]]]=&[&[b\"pool-authority\",mint.as_ref(),&pb]];")],
    'p_pool_neg': [(" if pool_updated{\n", " if !pool_updated{msg!(\"No canonical pump pool for this mint; curve only\");}else{\n"),
                   (" }else{msg!(\"No canonical pump pool for this mint; curve only\");}\n", " }\n")],
    'p_bump_inline_pool': [(" let pb=[ctx.bumps.pool_authority];let poolseeds:&[&[u8]]=&[b\"pool-authority\",mint.as_ref(),&pb];",
                            " let pb=ctx.bumps.pool_authority;let poolseeds:&[&[u8]]=&[b\"pool-authority\",mint.as_ref(),&[pb]];")],
}


def apply(names, src):
    s = src
    for n in names:
        for a, b in G[n]:
            c = s.count(a)
            if c != 1:
                raise ValueError(f'gene {n}: pattern count {c}: {a[:90]!r}')
            s = s.replace(a, b)
    if s.count('\n') != src.count('\n'):
        raise ValueError(f'genes {names}: newline count changed')
    return s


if __name__ == '__main__':
    import sys
    base = open(sys.argv[1]).read()
    bad = 0
    for n in G:
        try:
            out = apply([n], base)
            assert out != base, 'no change'
        except Exception as e:
            bad += 1
            print('BAD', n, e)
    print(len(G), 'genes,', bad, 'bad')
