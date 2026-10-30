EDITS=[
 ('fn validate(st:&CtoState,holder:bool,fee:Option<u64>,new:Option<Pubkey>,holder_key:&Pubkey,sharing:&Pubkey)->Result<Pubkey>{',
  'fn validate(st:&CtoState,holder:bool,fee:Option<u64>,new:Option<Pubkey>,holder_key:&Pubkey,sharing:&Pubkey)->Result<(Pubkey,Option<u64>)>{'),
 (' Ok(target)}pub fn execute(', ' Ok((target,fee))}pub fn execute('),
 ('let (holder,cashback,target,sharing_update,collect_old)={let st=', 'let (holder,cashback,target,fee,sharing_update,collect_old)={let st='),
 ('let mut target=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;', 'let (mut target,fee)=validate(&st,holder,fee,new,&holder_key,&a.sharing_config.key())?;'),
 ('(holder,cashback,target,sharing_update,collect_old)};let mut target=target;', '(holder,cashback,target,fee,sharing_update,collect_old)};let mut target=target;'),
]
