"use strict";(self.webpackChunkdocusaurus=self.webpackChunkdocusaurus||[]).push([[6209],{2118:(e,s,n)=>{n.r(s),n.d(s,{assets:()=>t,contentTitle:()=>d,default:()=>x,frontMatter:()=>l,metadata:()=>c,toc:()=>o});var r=n(4848),i=n(8453);const l={sidebar_position:5},d="Guardrails",c={id:"references/guardrails",title:"Guardrails",description:"A proxy server that applies guardrails to requests and responses.",source:"@site/content/references/guardrails.md",sourceDirName:"references",slug:"/references/guardrails",permalink:"/xrx-core/docs/references/guardrails",draft:!1,unlisted:!1,editUrl:"https://github.com/8090-inc/xrx-core/blob/main/docs/content/references/guardrails.md",tags:[],version:"current",sidebarPosition:5,frontMatter:{sidebar_position:5},sidebar:"tutorialSidebar",previous:{title:"Reasoning Agent",permalink:"/xrx-core/docs/references/agent"},next:{title:"Contributing to xRx",permalink:"/xrx-core/docs/contributing"}},t={},o=[{value:"Info",id:"info",level:2},{value:"Paths",id:"paths",level:2},{value:"<code>/ {path}</code>",id:"-path",level:3},{value:"PUT",id:"put",level:4},{value:"GET",id:"get",level:4},{value:"PATCH",id:"patch",level:4},{value:"OPTIONS",id:"options",level:4},{value:"POST",id:"post",level:4},{value:"DELETE",id:"delete",level:4},{value:"Components",id:"components",level:2},{value:"Schemas",id:"schemas",level:3},{value:"HTTPValidationError",id:"httpvalidationerror",level:4},{value:"ValidationError",id:"validationerror",level:4}];function h(e){const s={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",h4:"h4",li:"li",p:"p",strong:"strong",ul:"ul",...(0,i.R)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(s.h1,{id:"guardrails",children:"Guardrails"}),"\n",(0,r.jsx)(s.p,{children:"A proxy server that applies guardrails to requests and responses."}),"\n",(0,r.jsx)(s.h2,{id:"info",children:"Info"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Title:"})," Guardrails Proxy"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," A proxy server that applies guardrails to requests and responses."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Version:"})," 1.0.0"]}),"\n"]}),"\n",(0,r.jsx)(s.h2,{id:"paths",children:"Paths"}),"\n",(0,r.jsx)(s.h3,{id:"-path",children:(0,r.jsx)(s.code,{children:"/ {path}"})}),"\n",(0,r.jsx)(s.h4,{id:"put",children:"PUT"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"get",children:"GET"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"patch",children:"PATCH"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"options",children:"OPTIONS"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"post",children:"POST"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"delete",children:"DELETE"}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Summary:"})," Proxy Request"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Description:"})," Proxies incoming requests to the target server, applying guardrails if configured."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Args:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (str): The path of the incoming request."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"request"})," (Request): The incoming FastAPI request object."]}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Returns:"})," Response: The proxied response, potentially modified by guardrails."]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Parameters:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"path"})," (string, required): Path"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Responses:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"200"}),": Successful Response"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"422"}),": Validation Error"]}),"\n"]}),"\n",(0,r.jsx)(s.h2,{id:"components",children:"Components"}),"\n",(0,r.jsx)(s.h3,{id:"schemas",children:"Schemas"}),"\n",(0,r.jsx)(s.h4,{id:"httpvalidationerror",children:"HTTPValidationError"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Type:"})," object"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Title:"})," HTTPValidationError"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Properties:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"detail"})," (array of ",(0,r.jsx)(s.a,{href:"#validationerror",children:"ValidationError"}),"): Detail"]}),"\n"]}),"\n",(0,r.jsx)(s.h4,{id:"validationerror",children:"ValidationError"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Type:"})," object"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Required:"}),' ["loc", "msg", "type"]']}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Title:"})," ValidationError"]}),"\n"]}),"\n",(0,r.jsx)(s.p,{children:(0,r.jsx)(s.strong,{children:"Properties:"})}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"loc"})," (array of ",(0,r.jsx)(s.code,{children:"string"})," or ",(0,r.jsx)(s.code,{children:"integer"}),"): Location"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"msg"})," (string): Message"]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.code,{children:"type"})," (string): Error Type"]}),"\n"]})]})}function x(e={}){const{wrapper:s}={...(0,i.R)(),...e.components};return s?(0,r.jsx)(s,{...e,children:(0,r.jsx)(h,{...e})}):h(e)}},8453:(e,s,n)=>{n.d(s,{R:()=>d,x:()=>c});var r=n(6540);const i={},l=r.createContext(i);function d(e){const s=r.useContext(l);return r.useMemo((function(){return"function"==typeof e?e(s):{...s,...e}}),[s,e])}function c(e){let s;return s=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:d(e.components),r.createElement(l.Provider,{value:s},e.children)}}}]);