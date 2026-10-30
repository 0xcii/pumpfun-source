# CPI-form variants for admin_cto.rs (lane w12b12-cto-cpi). Each entry: list of (old, new) replacements.
SEEDLINE = ' let pb=[ctx.bumps.pool_authority];let poolseeds:&[&[u8]]=&[b"pool-authority",mint.as_ref(),&pb];let signer_seeds:&[&[&[u8]]]=&[poolseeds];'
SH_HEAD = 'crate::pump_fees::cpi::admin_cto_sharing_config(CpiContext::new_with_signer(a.pump_fees.to_account_info(),'
SH_ACC = 'crate::pump_fees::cpi::accounts::AdminCtoSharingConfig{pool_authority:a.pool_authority.to_account_info(),authority:a.admin_set_creator_authority.to_account_info(),global:a.global.to_account_info(),mint:a.mint.to_account_info(),sharing_config:a.sharing_config.to_account_info(),event_authority:a.pump_fees_event_authority.to_account_info(),program:a.pump_fees.to_account_info()}'
SH_TAIL = ',signer_seeds),val)?;'
PO_HEAD = 'crate::pump_amm::cpi::admin_cto_pool(CpiContext::new_with_signer(a.pump_amm.to_account_info(),'
PO_ACC = 'crate::pump_amm::cpi::accounts::AdminCtoPool{payer:a.admin_set_creator_authority.to_account_info(),global_config:a.amm_global_config.to_account_info(),pool:a.pool.to_account_info(),pool_authority:a.pool_authority.to_account_info(),system_program:a.system_program.to_account_info(),event_authority:a.pump_amm_event_authority.to_account_info(),program:a.pump_amm.to_account_info()}'
PO_TAIL = ',signer_seeds),target,holder,fee)?;'
SH = SH_HEAD + SH_ACC + SH_TAIL
PO = PO_HEAD + PO_ACC + PO_TAIL
INL = '&[&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]]]'

CC_HEAD = 'crate::pump_amm::cpi::collect_coin_creator_fee(CpiContext::new(a.pump_amm.to_account_info(),'
CC_ACC = 'crate::pump_amm::cpi::accounts::CollectCoinCreatorFee{quote_mint:a.quote_mint.to_account_info(),quote_token_program:a.quote_token_program.to_account_info(),coin_creator:a.current_creator.to_account_info(),coin_creator_vault_authority:a.coin_creator_vault_authority.to_account_info(),coin_creator_vault_ata:a.coin_creator_vault_ata.to_account_info(),coin_creator_token_account:a.current_creator_quote_token_account.to_account_info(),event_authority:a.pump_amm_event_authority.to_account_info(),program:a.pump_amm.to_account_info()}'
CC_TAIL = '))?;}'
TF_HEAD = 'crate::pump_amm::cpi::transfer_creator_fees_to_pump_v2(CpiContext::new(a.pump_amm.to_account_info(),'
TF_ACC = 'crate::pump_amm::cpi::accounts::TransferCreatorFeesToPumpV2{system_program:a.system_program.to_account_info(),quote_mint:a.quote_mint.to_account_info(),token_program:a.quote_token_program.to_account_info(),payer:a.admin_set_creator_authority.to_account_info(),associated_token_program:a.associated_token_program.to_account_info(),coin_creator:a.current_creator.to_account_info(),coin_creator_vault_authority:a.coin_creator_vault_authority.to_account_info(),coin_creator_vault_ata:a.coin_creator_vault_ata.to_account_info(),pump_creator_vault:a.creator_vault.to_account_info(),pump_creator_vault_ata:a.creator_vault_quote_token_account.to_account_info(),event_authority:a.pump_amm_event_authority.to_account_info(),program:a.pump_amm.to_account_info()}'
TF_TAIL = '))?;}'

V = {
    # seeds
    'seedsinline': [(SEEDLINE, ''), (SH_TAIL, ',' + INL + '),val)?;'), (PO_TAIL, ',' + INL + '),target,holder,fee)?;')],
    'seedsnested': [(SEEDLINE, ' let signer_seeds:&[&[&[u8]]]=&[&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]]];')],
    'seedsbumpref': [(SEEDLINE, ' let poolseeds:&[&[u8]]=&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]];let signer_seeds:&[&[&[u8]]]=&[poolseeds];')],
    'seedsarr': [(SEEDLINE, ' let pb=[ctx.bumps.pool_authority];let poolseeds=[b"pool-authority".as_ref(),mint.as_ref(),&pb];let signer_seeds=[&poolseeds[..]];'),
                 (SH_TAIL, ',&signer_seeds),val)?;'), (PO_TAIL, ',&signer_seeds),target,holder,fee)?;')],
    # with_signer
    'sws': [(SH, 'crate::pump_fees::cpi::admin_cto_sharing_config(CpiContext::new(a.pump_fees.to_account_info(),' + SH_ACC + ').with_signer(signer_seeds),val)?;')],
    'pws': [(PO, 'crate::pump_amm::cpi::admin_cto_pool(CpiContext::new(a.pump_amm.to_account_info(),' + PO_ACC + ').with_signer(signer_seeds),target,holder,fee)?;')],
    # let-bound accounts / ctx / program
    'shacclet': [(SH, 'let accounts=' + SH_ACC + ';crate::pump_fees::cpi::admin_cto_sharing_config(CpiContext::new_with_signer(a.pump_fees.to_account_info(),accounts' + SH_TAIL)],
    'shctxlet': [(SH, 'let cpi_ctx=CpiContext::new_with_signer(a.pump_fees.to_account_info(),' + SH_ACC + ',signer_seeds);crate::pump_fees::cpi::admin_cto_sharing_config(cpi_ctx,val)?;')],
    'shproglet': [(SH, 'let program=a.pump_fees.to_account_info();crate::pump_fees::cpi::admin_cto_sharing_config(CpiContext::new_with_signer(program,' + SH_ACC + SH_TAIL)],
    'poacclet': [(PO, 'let accounts=' + PO_ACC + ';crate::pump_amm::cpi::admin_cto_pool(CpiContext::new_with_signer(a.pump_amm.to_account_info(),accounts' + PO_TAIL)],
    'poctxlet': [(PO, 'let cpi_ctx=CpiContext::new_with_signer(a.pump_amm.to_account_info(),' + PO_ACC + ',signer_seeds);crate::pump_amm::cpi::admin_cto_pool(cpi_ctx,target,holder,fee)?;')],
    'poproglet': [(PO, 'let program=a.pump_amm.to_account_info();crate::pump_amm::cpi::admin_cto_pool(CpiContext::new_with_signer(program,' + PO_ACC + PO_TAIL)],
    # pool CPI args read back from the curve
    'pocurveargs': [(PO_TAIL, ',signer_seeds),a.bonding_curve.creator,a.bonding_curve.is_holder_reward,fee)?;')],
    'pocurvetarget': [(PO_TAIL, ',signer_seeds),a.bonding_curve.creator,holder,fee)?;')],
    # unsigned CPIs
    'ccctxlet': [(CC_HEAD + CC_ACC + CC_TAIL, 'let cpi_ctx=CpiContext::new(a.pump_amm.to_account_info(),' + CC_ACC + ');crate::pump_amm::cpi::collect_coin_creator_fee(cpi_ctx)?;}')],
    'tfctxlet': [(TF_HEAD + TF_ACC + TF_TAIL, 'let cpi_ctx=CpiContext::new(a.pump_amm.to_account_info(),' + TF_ACC + ');crate::pump_amm::cpi::transfer_creator_fees_to_pump_v2(cpi_ctx)?;}')],
}

# closure idioms (migrate.rs matched siblings): move |signer_seeds:&[&[&[u8]];1]| cpi(...)
PO_CLOS = 'let cto=move |signer_seeds:&[&[&[u8]];1]|crate::pump_amm::cpi::admin_cto_pool(CpiContext::new_with_signer(a.pump_amm.to_account_info(),' + PO_ACC + ',signer_seeds),target,holder,fee);'
SH_CLOS = 'let share=move |signer_seeds:&[&[&[u8]];1]|crate::pump_fees::cpi::admin_cto_sharing_config(CpiContext::new_with_signer(a.pump_fees.to_account_info(),' + SH_ACC + ',signer_seeds),val);'
V.update({
    'poclos': [(PO, PO_CLOS + 'cto(&[poolseeds])?;')],
    'poclosinl': [(PO, PO_CLOS + 'cto(&[&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]]])?;')],
    'shclos': [(SH, SH_CLOS + 'share(&[poolseeds])?;')],
    'shclosinl': [(SH, SH_CLOS + 'share(&[&[b"pool-authority",mint.as_ref(),&[ctx.bumps.pool_authority]]])?;')],
    'poclosret': [(PO, 'let cto=move |signer_seeds:&[&[&[u8]];1]|crate::pump_amm::cpi::admin_cto_pool(CpiContext::new_with_signer(a.pump_amm.to_account_info(),' + PO_ACC + ',signer_seeds),target,holder,fee);cto(&[poolseeds])?;')],
})

# wallet (collect_old) emission placement: emit_cpi! signer-seeds alloca (_117.i74) frame position
V.update({
    'walletinline': [(' if collect_old{wallet(&ctx)?;}fn wallet(ctx:&Context<AdminCto>)->Result<()>{let a=&ctx.accounts;if a.current_creator.executable{', ' if collect_old{let a=&ctx.accounts;if a.current_creator.executable{'),
                     ('\n }}Ok(())}\n let swept;', '\n }}}\n let swept;')],
    'walletinlalways': [('}fn wallet(ctx:&Context<AdminCto>)->Result<()>{', '}#[inline(always)]fn wallet(ctx:&Context<AdminCto>)->Result<()>{')],
    'walletinlhint': [('}fn wallet(ctx:&Context<AdminCto>)->Result<()>{', '}#[inline]fn wallet(ctx:&Context<AdminCto>)->Result<()>{')],
})

# target dataflow (pool-CPI arg): avoid the offset-1 Pubkey of Result<Pubkey>/ControlFlow (7/16/9 SROA split)
VSIG = 'fn validate(st:&CtoState,holder:bool,fee:Option<u64>,new:Option<Pubkey>,holder_key:&Pubkey,sharing:&Pubkey)->Result<Pubkey>{'
VCALL = 'let mut target=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;'
V.update({
    'tgtout': [(VSIG, 'fn validate(st:&CtoState,holder:bool,fee:Option<u64>,new:Option<Pubkey>,holder_key:&Pubkey,sharing:&Pubkey,out:&mut Pubkey)->Result<()>{'),
               (' Ok(target)}pub fn execute(', ' *out=target;Ok(())}pub fn execute('),
               (VCALL, 'let mut target=Pubkey::default();validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key(),&mut target)?;')],
    'tgtunit': [(VSIG, 'fn validate(st:&CtoState,holder:bool,fee:Option<u64>,new:Option<Pubkey>,holder_key:&Pubkey,sharing:&Pubkey)->Result<()>{'),
                (' Ok(target)}pub fn execute(', ' let _=target;Ok(())}pub fn execute('),
                (VCALL, 'validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;let mut target=if holder{holder_key}else{new.unwrap_or_default()};')],
    'tgtmatch': [(VCALL, 'let mut target=match validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key()){Ok(t)=>t,Err(e)=>return Err(e)};')],
})

# new main (k4 region2_tree): sharing CPI `val` built from the validated target (orig: val [1,8)/[24,33) are copies
# of the new-creator-branch target pieces at the validation join), not from the `new` arg
V.update({
    'shvalt': [('else{target=st.creator;(Some(new),false)}', 'else{let t=target;target=st.creator;(Some(Some(t)),false)}')],
    'shvalt2': [('else{target=st.creator;(Some(new),false)}', 'else{let su=(Some(Some(target)),false);target=st.creator;su}')],
})
