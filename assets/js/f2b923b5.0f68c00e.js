"use strict";(self.webpackChunkdocusaurus=self.webpackChunkdocusaurus||[]).push([[1762],{1354:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>c,contentTitle:()=>a,default:()=>p,frontMatter:()=>r,metadata:()=>s,toc:()=>l});var i=t(4848),o=t(8453);const r={sidebar_position:3},a="Run the Patient Intake Application",s={id:"tutorials/run_patient_intake_application",title:"Run the Patient Intake Application",description:"This application provides an audio and visual experience for gathering information from a patient before they enter a doctor's office. As you talk, the screen fills in with the details you share, making reviewing your information easy in addition to verbal confirmation.",source:"@site/content/tutorials/run_patient_intake_application.md",sourceDirName:"tutorials",slug:"/tutorials/run_patient_intake_application",permalink:"/xrx-core/docs/tutorials/run_patient_intake_application",draft:!1,unlisted:!1,editUrl:"https://github.com/8090-inc/xrx-core/blob/develop/docs/content/tutorials/run_patient_intake_application.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Run the Shopify Application",permalink:"/xrx-core/docs/tutorials/run_shopify_applications"},next:{title:"Build Your Own Reasoning Application",permalink:"/xrx-core/docs/tutorials/bring_your_own_reasoning_agent"}},c={},l=[{value:"Check Redis Integration",id:"check-redis-integration",level:2},{value:"Deploy the Containers",id:"deploy-the-containers",level:2}];function d(e){const n={blockquote:"blockquote",code:"code",em:"em",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...(0,o.R)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(n.h1,{id:"run-the-patient-intake-application",children:"Run the Patient Intake Application"}),"\n",(0,i.jsx)(n.p,{children:"This application provides an audio and visual experience for gathering information from a patient before they enter a doctor's office. As you talk, the screen fills in with the details you share, making reviewing your information easy in addition to verbal confirmation."}),"\n",(0,i.jsxs)(n.blockquote,{children:["\n",(0,i.jsxs)(n.p,{children:[(0,i.jsx)(n.strong,{children:"Note:"})," For additional information and details about the Patient Intake application, please refer to the Patient Intake README file in the repository."]}),"\n"]}),"\n",(0,i.jsx)(n.h2,{id:"check-redis-integration",children:"Check Redis Integration"}),"\n",(0,i.jsx)(n.p,{children:(0,i.jsxs)(n.em,{children:["No action is needed for this section if you are using the docker-compose setup and pre-provided ",(0,i.jsx)(n.code,{children:".env"})," file."]})}),"\n",(0,i.jsx)(n.p,{children:"The Shopify agent uses a Redis container (xrx-redis) to shop and manage task statuses. This allows for efficient, real-time status updates and checks across the distributed system."}),"\n",(0,i.jsx)(n.p,{children:"If you are using the docker-compose setup, the Redis container will be automatically started and the reasoning agent will be able to use it as long as the environment variable is correctly set as shown below."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{children:'REDIS_HOST="xrx-redis"\n'})}),"\n",(0,i.jsxs)(n.p,{children:["If you are running the agent locally outside of docker compose, the reasoning agent will look for a Redis container on the default host (",(0,i.jsx)(n.code,{children:"localhost"}),") and port (",(0,i.jsx)(n.code,{children:"6379"}),"). In order to start that server, you can use the following command:"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{children:"docker run -d --name redis-server -p 6379:6379 redis\n"})}),"\n",(0,i.jsx)(n.h2,{id:"deploy-the-containers",children:"Deploy the Containers"}),"\n",(0,i.jsx)(n.p,{children:"Once you have completed the above step, you can deploy the containers by running the following command:"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{children:"docker compose up --build\n"})}),"\n",(0,i.jsx)(n.p,{children:"This use case is super simple and ready to be deployed.\nEnjoy experimenting!"})]})}function p(e={}){const{wrapper:n}={...(0,o.R)(),...e.components};return n?(0,i.jsx)(n,{...e,children:(0,i.jsx)(d,{...e})}):d(e)}},8453:(e,n,t)=>{t.d(n,{R:()=>a,x:()=>s});var i=t(6540);const o={},r=i.createContext(o);function a(e){const n=i.useContext(r);return i.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:a(e.components),i.createElement(r.Provider,{value:n},e.children)}}}]);