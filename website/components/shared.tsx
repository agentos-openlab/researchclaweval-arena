export function PageIntro({label,title,children}:{label:string,title:string,children:React.ReactNode}){return <div className="page-intro"><div className="eyebrow">{label}</div><h1>{title}</h1><p>{children}</p></div>}
export function Notice({children}:{children:React.ReactNode}){return <div className="notice"><span>i</span><div>{children}</div></div>}
