EDITS=[
 ('let (holder,cashback,target,sharing_update,collect_old)={let st=CtoState{',
  'let (holder,cashback,target,fee,sharing_update,collect_old)=(||->Result<(bool,bool,Pubkey,Option<u64>,Option<Option<Pubkey>>,bool)>{let st=CtoState{'),
 ('if shared&&!holder{target=st.creator;}(holder,cashback,target,sharing_update,collect_old)};let mut target=target;',
  'if shared&&!holder{target=st.creator;}Ok((holder,cashback,target,fee,sharing_update,collect_old))})()?;let mut target=target;'),
]
