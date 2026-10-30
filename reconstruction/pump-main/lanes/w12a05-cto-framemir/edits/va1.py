OLD_SIG='pub fn execute(ctx:Context<AdminCto>,holder:Option<bool>,fee:Option<u64>,new:Option<Pubkey>)->Result<()>{'
NEW_SIG='pub fn execute(ctx:Context<AdminCto>,holder_arg:Option<bool>,fee:Option<u64>,new:Option<Pubkey>)->Result<()>{'
OLD_BLK='let (holder,cashback,target,sharing_update,collect_old)={let st=CtoState{'
NEW_BLK='let (holder,cashback,mut target,sharing_update,collect_old);{let st=CtoState{'
OLD_IN=' let holder=holder==Some(true);let cashback=!holder&&st.cashback;let mut target=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;let sharing_update=if shared{Some(if holder{None}else{new})}else{None};let collect_old=!shared&&!st.holder_reward&&st.creator!=Pubkey::default();if shared&&!holder{target=st.creator;}(holder,cashback,target,sharing_update,collect_old)};let mut target=target;'
NEW_IN=' holder=holder_arg==Some(true);cashback=!holder&&st.cashback;target=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;sharing_update=if shared{Some(if holder{None}else{new})}else{None};collect_old=!shared&&!st.holder_reward&&st.creator!=Pubkey::default();if shared&&!holder{target=st.creator;}}'
EDITS=[(OLD_SIG,NEW_SIG),(OLD_BLK,NEW_BLK),(OLD_IN,NEW_IN)]
