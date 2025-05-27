import{r as d,a as J,R as B,B as Z}from"./vendor-C56AVnVk.js";import{C as G,a as K,L as X,P as Q,b as ee,p as te,c as re,d as ae,i as se,e as oe}from"./charts-Dm2hZXDp.js";(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const i of document.querySelectorAll('link[rel="modulepreload"]'))o(i);new MutationObserver(i=>{for(const s of i)if(s.type==="childList")for(const l of s.addedNodes)l.tagName==="LINK"&&l.rel==="modulepreload"&&o(l)}).observe(document,{childList:!0,subtree:!0});function a(i){const s={};return i.integrity&&(s.integrity=i.integrity),i.referrerPolicy&&(s.referrerPolicy=i.referrerPolicy),i.crossOrigin==="use-credentials"?s.credentials="include":i.crossOrigin==="anonymous"?s.credentials="omit":s.credentials="same-origin",s}function o(i){if(i.ep)return;i.ep=!0;const s=a(i);fetch(i.href,s)}})();var H={exports:{}},$={};/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ie=d,ne=Symbol.for("react.element"),le=Symbol.for("react.fragment"),de=Object.prototype.hasOwnProperty,ce=ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,ue={key:!0,ref:!0,__self:!0,__source:!0};function U(e,t,a){var o,i={},s=null,l=null;a!==void 0&&(s=""+a),t.key!==void 0&&(s=""+t.key),t.ref!==void 0&&(l=t.ref);for(o in t)de.call(t,o)&&!ue.hasOwnProperty(o)&&(i[o]=t[o]);if(e&&e.defaultProps)for(o in t=e.defaultProps,t)i[o]===void 0&&(i[o]=t[o]);return{$$typeof:ne,type:e,key:s,ref:l,props:i,_owner:ce.current}}$.Fragment=le;$.jsx=U;$.jsxs=U;H.exports=$;var r=H.exports,A={},F=J;A.createRoot=F.createRoot,A.hydrateRoot=F.hydrateRoot;let me={data:""},pe=e=>typeof window=="object"?((e?e.querySelector("#_goober"):window._goober)||Object.assign((e||document.head).appendChild(document.createElement("style")),{innerHTML:" ",id:"_goober"})).firstChild:e||me,ge=/(?:([\u0080-\uFFFF\w-%@]+) *:? *([^{;]+?);|([^;}{]*?) *{)|(}\s*)/g,xe=/\/\*[^]*?\*\/|  +/g,I=/\n+/g,v=(e,t)=>{let a="",o="",i="";for(let s in e){let l=e[s];s[0]=="@"?s[1]=="i"?a=s+" "+l+";":o+=s[1]=="f"?v(l,s):s+"{"+v(l,s[1]=="k"?"":t)+"}":typeof l=="object"?o+=v(l,t?t.replace(/([^,])+/g,n=>s.replace(/([^,]*:\S+\([^)]*\))|([^,])+/g,u=>/&/.test(u)?u.replace(/&/g,n):n?n+" "+u:u)):s):l!=null&&(s=/^--/.test(s)?s:s.replace(/[A-Z]/g,"-$&").toLowerCase(),i+=v.p?v.p(s,l):s+":"+l+";")}return a+(t&&i?t+"{"+i+"}":i)+o},b={},W=e=>{if(typeof e=="object"){let t="";for(let a in e)t+=a+W(e[a]);return t}return e},he=(e,t,a,o,i)=>{let s=W(e),l=b[s]||(b[s]=(u=>{let m=0,c=11;for(;m<u.length;)c=101*c+u.charCodeAt(m++)>>>0;return"go"+c})(s));if(!b[l]){let u=s!==e?e:(m=>{let c,h,p=[{}];for(;c=ge.exec(m.replace(xe,""));)c[4]?p.shift():c[3]?(h=c[3].replace(I," ").trim(),p.unshift(p[0][h]=p[0][h]||{})):p[0][c[1]]=c[2].replace(I," ").trim();return p[0]})(e);b[l]=v(i?{["@keyframes "+l]:u}:u,a?"":"."+l)}let n=a&&b.g?b.g:null;return a&&(b.g=b[l]),((u,m,c,h)=>{h?m.data=m.data.replace(h,u):m.data.indexOf(u)===-1&&(m.data=c?u+m.data:m.data+u)})(b[l],t,o,n),l},fe=(e,t,a)=>e.reduce((o,i,s)=>{let l=t[s];if(l&&l.call){let n=l(a),u=n&&n.props&&n.props.className||/^go/.test(n)&&n;l=u?"."+u:n&&typeof n=="object"?n.props?"":v(n,""):n===!1?"":n}return o+i+(l??"")},"");function D(e){let t=this||{},a=e.call?e(t.p):e;return he(a.unshift?a.raw?fe(a,[].slice.call(arguments,1),t.p):a.reduce((o,i)=>Object.assign(o,i&&i.call?i(t.p):i),{}):a,pe(t.target),t.g,t.o,t.k)}let V,_,z;D.bind({g:1});let y=D.bind({k:1});function be(e,t,a,o){v.p=t,V=e,_=a,z=o}function k(e,t){let a=this||{};return function(){let o=arguments;function i(s,l){let n=Object.assign({},s),u=n.className||i.className;a.p=Object.assign({theme:_&&_()},n),a.o=/ *go\d+/.test(u),n.className=D.apply(a,o)+(u?" "+u:"");let m=e;return e[0]&&(m=n.as||e,delete n.as),z&&m[0]&&z(n),V(m,n)}return i}}var ye=e=>typeof e=="function",P=(e,t)=>ye(e)?e(t):e,ve=(()=>{let e=0;return()=>(++e).toString()})(),Y=(()=>{let e;return()=>{if(e===void 0&&typeof window<"u"){let t=matchMedia("(prefers-reduced-motion: reduce)");e=!t||t.matches}return e}})(),ke=20,q=(e,t)=>{switch(t.type){case 0:return{...e,toasts:[t.toast,...e.toasts].slice(0,ke)};case 1:return{...e,toasts:e.toasts.map(s=>s.id===t.toast.id?{...s,...t.toast}:s)};case 2:let{toast:a}=t;return q(e,{type:e.toasts.find(s=>s.id===a.id)?1:0,toast:a});case 3:let{toastId:o}=t;return{...e,toasts:e.toasts.map(s=>s.id===o||o===void 0?{...s,dismissed:!0,visible:!1}:s)};case 4:return t.toastId===void 0?{...e,toasts:[]}:{...e,toasts:e.toasts.filter(s=>s.id!==t.toastId)};case 5:return{...e,pausedAt:t.time};case 6:let i=t.time-(e.pausedAt||0);return{...e,pausedAt:void 0,toasts:e.toasts.map(s=>({...s,pauseDuration:s.pauseDuration+i}))}}},L=[],j={toasts:[],pausedAt:void 0},w=e=>{j=q(j,e),L.forEach(t=>{t(j)})},je={blank:4e3,error:4e3,success:2e3,loading:1/0,custom:4e3},we=(e={})=>{let[t,a]=d.useState(j),o=d.useRef(j);d.useEffect(()=>(o.current!==j&&a(j),L.push(a),()=>{let s=L.indexOf(a);s>-1&&L.splice(s,1)}),[]);let i=t.toasts.map(s=>{var l,n,u;return{...e,...e[s.type],...s,removeDelay:s.removeDelay||((l=e[s.type])==null?void 0:l.removeDelay)||(e==null?void 0:e.removeDelay),duration:s.duration||((n=e[s.type])==null?void 0:n.duration)||(e==null?void 0:e.duration)||je[s.type],style:{...e.style,...(u=e[s.type])==null?void 0:u.style,...s.style}}});return{...t,toasts:i}},Ne=(e,t="blank",a)=>({createdAt:Date.now(),visible:!0,dismissed:!1,type:t,ariaProps:{role:"status","aria-live":"polite"},message:e,pauseDuration:0,...a,id:(a==null?void 0:a.id)||ve()}),C=e=>(t,a)=>{let o=Ne(t,e,a);return w({type:2,toast:o}),o.id},f=(e,t)=>C("blank")(e,t);f.error=C("error");f.success=C("success");f.loading=C("loading");f.custom=C("custom");f.dismiss=e=>{w({type:3,toastId:e})};f.remove=e=>w({type:4,toastId:e});f.promise=(e,t,a)=>{let o=f.loading(t.loading,{...a,...a==null?void 0:a.loading});return typeof e=="function"&&(e=e()),e.then(i=>{let s=t.success?P(t.success,i):void 0;return s?f.success(s,{id:o,...a,...a==null?void 0:a.success}):f.dismiss(o),i}).catch(i=>{let s=t.error?P(t.error,i):void 0;s?f.error(s,{id:o,...a,...a==null?void 0:a.error}):f.dismiss(o)}),e};var Se=(e,t)=>{w({type:1,toast:{id:e,height:t}})},Ce=()=>{w({type:5,time:Date.now()})},S=new Map,Ee=1e3,Le=(e,t=Ee)=>{if(S.has(e))return;let a=setTimeout(()=>{S.delete(e),w({type:4,toastId:e})},t);S.set(e,a)},Pe=e=>{let{toasts:t,pausedAt:a}=we(e);d.useEffect(()=>{if(a)return;let s=Date.now(),l=t.map(n=>{if(n.duration===1/0)return;let u=(n.duration||0)+n.pauseDuration-(s-n.createdAt);if(u<0){n.visible&&f.dismiss(n.id);return}return setTimeout(()=>f.dismiss(n.id),u)});return()=>{l.forEach(n=>n&&clearTimeout(n))}},[t,a]);let o=d.useCallback(()=>{a&&w({type:6,time:Date.now()})},[a]),i=d.useCallback((s,l)=>{let{reverseOrder:n=!1,gutter:u=8,defaultPosition:m}=l||{},c=t.filter(g=>(g.position||m)===(s.position||m)&&g.height),h=c.findIndex(g=>g.id===s.id),p=c.filter((g,x)=>x<h&&g.visible).length;return c.filter(g=>g.visible).slice(...n?[p+1]:[0,p]).reduce((g,x)=>g+(x.height||0)+u,0)},[t]);return d.useEffect(()=>{t.forEach(s=>{if(s.dismissed)Le(s.id,s.removeDelay);else{let l=S.get(s.id);l&&(clearTimeout(l),S.delete(s.id))}})},[t]),{toasts:t,handlers:{updateHeight:Se,startPause:Ce,endPause:o,calculateOffset:i}}},$e=y`
from {
  transform: scale(0) rotate(45deg);
	opacity: 0;
}
to {
 transform: scale(1) rotate(45deg);
  opacity: 1;
}`,De=y`
from {
  transform: scale(0);
  opacity: 0;
}
to {
  transform: scale(1);
  opacity: 1;
}`,Re=y`
from {
  transform: scale(0) rotate(90deg);
	opacity: 0;
}
to {
  transform: scale(1) rotate(90deg);
	opacity: 1;
}`,Oe=k("div")`
  width: 20px;
  opacity: 0;
  height: 20px;
  border-radius: 10px;
  background: ${e=>e.primary||"#ff4b4b"};
  position: relative;
  transform: rotate(45deg);

  animation: ${$e} 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
  animation-delay: 100ms;

  &:after,
  &:before {
    content: '';
    animation: ${De} 0.15s ease-out forwards;
    animation-delay: 150ms;
    position: absolute;
    border-radius: 3px;
    opacity: 0;
    background: ${e=>e.secondary||"#fff"};
    bottom: 9px;
    left: 4px;
    height: 2px;
    width: 12px;
  }

  &:before {
    animation: ${Re} 0.15s ease-out forwards;
    animation-delay: 180ms;
    transform: rotate(90deg);
  }
`,Ae=y`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`,_e=k("div")`
  width: 12px;
  height: 12px;
  box-sizing: border-box;
  border: 2px solid;
  border-radius: 100%;
  border-color: ${e=>e.secondary||"#e0e0e0"};
  border-right-color: ${e=>e.primary||"#616161"};
  animation: ${Ae} 1s linear infinite;
`,ze=y`
from {
  transform: scale(0) rotate(45deg);
	opacity: 0;
}
to {
  transform: scale(1) rotate(45deg);
	opacity: 1;
}`,Me=y`
0% {
	height: 0;
	width: 0;
	opacity: 0;
}
40% {
  height: 0;
	width: 6px;
	opacity: 1;
}
100% {
  opacity: 1;
  height: 10px;
}`,Fe=k("div")`
  width: 20px;
  opacity: 0;
  height: 20px;
  border-radius: 10px;
  background: ${e=>e.primary||"#61d345"};
  position: relative;
  transform: rotate(45deg);

  animation: ${ze} 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
  animation-delay: 100ms;
  &:after {
    content: '';
    box-sizing: border-box;
    animation: ${Me} 0.2s ease-out forwards;
    opacity: 0;
    animation-delay: 200ms;
    position: absolute;
    border-right: 2px solid;
    border-bottom: 2px solid;
    border-color: ${e=>e.secondary||"#fff"};
    bottom: 6px;
    left: 6px;
    height: 10px;
    width: 6px;
  }
`,Ie=k("div")`
  position: absolute;
`,Te=k("div")`
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 20px;
  min-height: 20px;
`,Be=y`
from {
  transform: scale(0.6);
  opacity: 0.4;
}
to {
  transform: scale(1);
  opacity: 1;
}`,He=k("div")`
  position: relative;
  transform: scale(0.6);
  opacity: 0.4;
  min-width: 20px;
  animation: ${Be} 0.3s 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
`,Ue=({toast:e})=>{let{icon:t,type:a,iconTheme:o}=e;return t!==void 0?typeof t=="string"?d.createElement(He,null,t):t:a==="blank"?null:d.createElement(Te,null,d.createElement(_e,{...o}),a!=="loading"&&d.createElement(Ie,null,a==="error"?d.createElement(Oe,{...o}):d.createElement(Fe,{...o})))},We=e=>`
0% {transform: translate3d(0,${e*-200}%,0) scale(.6); opacity:.5;}
100% {transform: translate3d(0,0,0) scale(1); opacity:1;}
`,Ve=e=>`
0% {transform: translate3d(0,0,-1px) scale(1); opacity:1;}
100% {transform: translate3d(0,${e*-150}%,-1px) scale(.6); opacity:0;}
`,Ye="0%{opacity:0;} 100%{opacity:1;}",qe="0%{opacity:1;} 100%{opacity:0;}",Je=k("div")`
  display: flex;
  align-items: center;
  background: #fff;
  color: #363636;
  line-height: 1.3;
  will-change: transform;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1), 0 3px 3px rgba(0, 0, 0, 0.05);
  max-width: 350px;
  pointer-events: auto;
  padding: 8px 10px;
  border-radius: 8px;
`,Ze=k("div")`
  display: flex;
  justify-content: center;
  margin: 4px 10px;
  color: inherit;
  flex: 1 1 auto;
  white-space: pre-line;
`,Ge=(e,t)=>{let a=e.includes("top")?1:-1,[o,i]=Y()?[Ye,qe]:[We(a),Ve(a)];return{animation:t?`${y(o)} 0.35s cubic-bezier(.21,1.02,.73,1) forwards`:`${y(i)} 0.4s forwards cubic-bezier(.06,.71,.55,1)`}},Ke=d.memo(({toast:e,position:t,style:a,children:o})=>{let i=e.height?Ge(e.position||t||"top-center",e.visible):{opacity:0},s=d.createElement(Ue,{toast:e}),l=d.createElement(Ze,{...e.ariaProps},P(e.message,e));return d.createElement(Je,{className:e.className,style:{...i,...a,...e.style}},typeof o=="function"?o({icon:s,message:l}):d.createElement(d.Fragment,null,s,l))});be(d.createElement);var Xe=({id:e,className:t,style:a,onHeightUpdate:o,children:i})=>{let s=d.useCallback(l=>{if(l){let n=()=>{let u=l.getBoundingClientRect().height;o(e,u)};n(),new MutationObserver(n).observe(l,{subtree:!0,childList:!0,characterData:!0})}},[e,o]);return d.createElement("div",{ref:s,className:t,style:a},i)},Qe=(e,t)=>{let a=e.includes("top"),o=a?{top:0}:{bottom:0},i=e.includes("center")?{justifyContent:"center"}:e.includes("right")?{justifyContent:"flex-end"}:{};return{left:0,right:0,display:"flex",position:"absolute",transition:Y()?void 0:"all 230ms cubic-bezier(.21,1.02,.73,1)",transform:`translateY(${t*(a?1:-1)}px)`,...o,...i}},et=D`
  z-index: 9999;
  > * {
    pointer-events: auto;
  }
`,E=16,tt=({reverseOrder:e,position:t="top-center",toastOptions:a,gutter:o,children:i,containerStyle:s,containerClassName:l})=>{let{toasts:n,handlers:u}=Pe(a);return d.createElement("div",{id:"_rht_toaster",style:{position:"fixed",zIndex:9999,top:E,left:E,right:E,bottom:E,pointerEvents:"none",...s},className:l,onMouseEnter:u.startPause,onMouseLeave:u.endPause},n.map(m=>{let c=m.position||t,h=u.calculateOffset(m,{reverseOrder:e,gutter:o,defaultPosition:t}),p=Qe(c,h);return d.createElement(Xe,{id:m.id,key:m.id,onHeightUpdate:u.updateHeight,className:m.visible?et:"",style:p},m.type==="custom"?P(m.message,m):i?i(m):d.createElement(Ke,{toast:m,position:c}))}))},N=f;function rt({title:e,titleId:t,...a},o){return d.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",fill:"none",viewBox:"0 0 24 24",strokeWidth:1.5,stroke:"currentColor","aria-hidden":"true","data-slot":"icon",ref:o,"aria-labelledby":t},a),e?d.createElement("title",{id:t},e):null,d.createElement("path",{strokeLinecap:"round",strokeLinejoin:"round",d:"M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"}))}const at=d.forwardRef(rt);function st({title:e,titleId:t,...a},o){return d.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",fill:"none",viewBox:"0 0 24 24",strokeWidth:1.5,stroke:"currentColor","aria-hidden":"true","data-slot":"icon",ref:o,"aria-labelledby":t},a),e?d.createElement("title",{id:t},e):null,d.createElement("path",{strokeLinecap:"round",strokeLinejoin:"round",d:"M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"}))}const ot=d.forwardRef(st),it=()=>{const[e,t]=d.useState(!1),a=()=>{t(!e),document.documentElement.classList.toggle("dark")};return r.jsx("header",{className:"sticky top-0 z-50 bg-white dark:bg-gray-900 shadow-sm",children:r.jsx("div",{className:"container mx-auto px-4 py-4",children:r.jsxs("div",{className:"flex items-center justify-between",children:[r.jsxs("div",{className:"flex items-center space-x-2",children:[r.jsx("h1",{className:"text-2xl font-bold text-blue-600 dark:text-blue-400",children:"PricePulse"}),r.jsx("span",{className:"text-sm text-gray-600 dark:text-gray-400",children:"Track prices. Compare smartly."})]}),r.jsx("button",{onClick:a,className:"p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors","aria-label":"Toggle theme",children:e?r.jsx(ot,{className:"h-6 w-6 text-yellow-500"}):r.jsx(at,{className:"h-6 w-6 text-gray-600"})})]})})})},M=({size:e="md",text:t,className:a=""})=>{const o={sm:"h-4 w-4 border-2",md:"h-8 w-8 border-2",lg:"h-12 w-12 border-3"};return r.jsxs("div",{className:`flex items-center justify-center ${a}`,children:[r.jsx("div",{className:`animate-spin rounded-full border-b-2 border-blue-600 dark:border-blue-400 ${o[e]}`}),t&&r.jsx("span",{className:"ml-2 text-sm text-gray-600 dark:text-gray-400",children:t})]})},nt=({onSubmit:e})=>{const[t,a]=d.useState(""),[o,i]=d.useState(""),[s,l]=d.useState(""),[n,u]=d.useState(!1),m=p=>{try{const g=new URL(p);return g.hostname.includes("amazon.in")||g.hostname.includes("amazon.com")}catch{return!1}},c=p=>p?/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p):!0,h=async p=>{if(p.preventDefault(),!m(t)){N.error("Please enter a valid Amazon URL");return}if(!c(s)){N.error("Please enter a valid email address");return}if(o&&(isNaN(Number(o))||Number(o)<=0)){N.error("Please enter a valid target price");return}try{u(!0),await e({url:t,targetPrice:o?parseFloat(o):void 0,email:s||void 0}),N.success("Product tracking started successfully!")}catch(g){N.error("Failed to start tracking. Please try again."),console.error("Error submitting product:",g)}finally{u(!1)}};return r.jsx("div",{className:"bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",children:r.jsxs("form",{onSubmit:h,className:"space-y-4",children:[r.jsxs("div",{children:[r.jsx("label",{htmlFor:"url",className:"block text-sm font-medium text-gray-700 dark:text-gray-300",children:"Amazon Product URL"}),r.jsx("input",{type:"url",id:"url",value:t,onChange:p=>a(p.target.value),placeholder:"https://www.amazon.in/product...",required:!0,disabled:n,className:"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"})]}),r.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-4",children:[r.jsxs("div",{children:[r.jsx("label",{htmlFor:"targetPrice",className:"block text-sm font-medium text-gray-700 dark:text-gray-300",children:"Target Price (₹)"}),r.jsx("input",{type:"number",id:"targetPrice",value:o,onChange:p=>i(p.target.value),placeholder:"999",min:"0",step:"0.01",disabled:n,className:"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"})]}),r.jsxs("div",{children:[r.jsx("label",{htmlFor:"email",className:"block text-sm font-medium text-gray-700 dark:text-gray-300",children:"Your Email (Optional)"}),r.jsx("input",{type:"email",id:"email",value:s,onChange:p=>l(p.target.value),placeholder:"you@example.com",disabled:n,className:"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"})]})]}),r.jsx("button",{type:"submit",disabled:n,className:"w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed",children:n?r.jsxs("div",{className:"flex items-center justify-center",children:[r.jsx(M,{}),r.jsx("span",{className:"ml-2",children:"Processing..."})]}):"Track Product"})]})})},lt=({image:e,title:t,currentPrice:a,amazonUrl:o,status:i})=>{const s=()=>{const l={tracking:"bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",alert_set:"bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",price_drop:"bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"},n={tracking:"Tracking...",alert_set:"Price Drop Alert Set",price_drop:"Price Drop Alert Sent!"};return r.jsx("span",{className:`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${l[i]}`,children:n[i]})};return r.jsx("div",{className:"bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",children:r.jsxs("div",{className:"flex flex-col md:flex-row gap-6",children:[r.jsx("div",{className:"w-full md:w-1/3",children:r.jsx("img",{src:e,alt:t,className:"w-full h-48 object-contain rounded-lg bg-gray-50 dark:bg-gray-700"})}),r.jsxs("div",{className:"flex-1 space-y-4",children:[r.jsxs("div",{children:[r.jsx("h2",{className:"text-xl font-semibold text-gray-900 dark:text-white",children:t}),s()]}),r.jsxs("div",{className:"text-2xl font-bold text-blue-600 dark:text-blue-400",children:["₹",a.toLocaleString()]}),r.jsxs("a",{href:o,target:"_blank",rel:"noopener noreferrer",className:"inline-flex items-center text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300",children:["View on Amazon",r.jsx("svg",{className:"ml-1 w-4 h-4",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"})})]})]})]})})};G.register(K,X,Q,ee,te,re,ae,se);const dt=({data:e,onRefresh:t})=>{const a={labels:e.map(i=>new Date(i.date).toLocaleDateString()),datasets:[{label:"Price History",data:e.map(i=>i.price),borderColor:"rgb(59, 130, 246)",backgroundColor:"rgba(59, 130, 246, 0.1)",tension:.4,fill:!0,pointRadius:4,pointHoverRadius:6,pointBackgroundColor:"rgb(59, 130, 246)",pointBorderColor:"#fff",pointBorderWidth:2}]},o={responsive:!0,maintainAspectRatio:!1,interaction:{mode:"index",intersect:!1},plugins:{legend:{position:"top",labels:{color:"rgb(156, 163, 175)",font:{size:12}}},title:{display:!0,text:"Price History",color:"rgb(156, 163, 175)",font:{size:16,weight:"bold"}},tooltip:{backgroundColor:"rgba(0, 0, 0, 0.8)",titleColor:"#fff",bodyColor:"#fff",borderColor:"rgba(255, 255, 255, 0.1)",borderWidth:1,padding:12,displayColors:!1,callbacks:{label:i=>`₹${i.parsed.y.toLocaleString()}`}}},scales:{x:{grid:{color:"rgba(156, 163, 175, 0.1)"},ticks:{color:"rgb(156, 163, 175)",maxRotation:45,minRotation:45}},y:{beginAtZero:!1,grid:{color:"rgba(156, 163, 175, 0.1)"},ticks:{color:"rgb(156, 163, 175)",callback:i=>`₹${i.toLocaleString()}`}}}};return r.jsxs("div",{className:"bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",children:[r.jsxs("div",{className:"flex justify-between items-center mb-4",children:[r.jsx("h3",{className:"text-lg font-semibold text-gray-900 dark:text-white",children:"Price Trend"}),t&&r.jsxs("button",{onClick:t,className:"inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors",children:[r.jsx("svg",{className:"w-4 h-4 mr-1",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"})}),"Refresh Data"]})]}),r.jsx("div",{className:"h-80",children:r.jsx(oe,{data:a,options:o})})]})},ct=({prices:e})=>{const[t,a]=d.useState("price"),[o,i]=d.useState("asc"),[s,l]=d.useState(""),n=c=>{c===t?i(o==="asc"?"desc":"asc"):(a(c),i("asc"))},u=e.filter(c=>Object.values(c).some(h=>h.toString().toLowerCase().includes(s.toLowerCase()))).sort((c,h)=>{const p=c[t],g=h[t],x=o==="asc"?1:-1;return typeof p=="string"&&typeof g=="string"?p.localeCompare(g)*x:(p-g)*x}),m=({field:c})=>c!==t?null:r.jsx("svg",{className:`w-4 h-4 ml-1 inline-block ${o==="asc"?"transform rotate-180":""}`,fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M19 9l-7 7-7-7"})});return r.jsxs("div",{className:"bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",children:[r.jsxs("div",{className:"flex flex-col md:flex-row justify-between items-center mb-4",children:[r.jsx("h3",{className:"text-lg font-semibold text-gray-900 dark:text-white mb-4 md:mb-0",children:"Cross-Platform Comparison"}),r.jsx("div",{className:"w-full md:w-64",children:r.jsx("input",{type:"text",placeholder:"Search...",value:s,onChange:c=>l(c.target.value),className:"w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"})})]}),r.jsx("div",{className:"overflow-x-auto",children:r.jsxs("table",{className:"min-w-full divide-y divide-gray-200 dark:divide-gray-700",children:[r.jsx("thead",{className:"bg-gray-50 dark:bg-gray-700",children:r.jsx("tr",{children:["platform","title","price","url"].map(c=>r.jsx("th",{scope:"col",className:"px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600",onClick:()=>n(c),children:r.jsxs("div",{className:"flex items-center",children:[c.charAt(0).toUpperCase()+c.slice(1),r.jsx(m,{field:c})]})},c))})}),r.jsx("tbody",{className:"bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700",children:u.map((c,h)=>r.jsxs("tr",{className:"hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors",children:[r.jsx("td",{className:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white",children:c.platform}),r.jsx("td",{className:"px-6 py-4 text-sm text-gray-500 dark:text-gray-300",children:c.title}),r.jsxs("td",{className:"px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300",children:["₹",c.price.toLocaleString()]}),r.jsx("td",{className:"px-6 py-4 whitespace-nowrap text-sm",children:r.jsxs("a",{href:c.url,target:"_blank",rel:"noopener noreferrer",className:"inline-flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300",children:["View",r.jsx("svg",{className:"ml-1 w-4 h-4",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"})})]})})]},h))})]})})]})},ut=({targetPrice:e,email:t,isPriceDrop:a})=>!e&&!t&&!a?null:r.jsx("div",{className:"bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animate-fade-in",children:r.jsx("div",{className:"flex items-center space-x-3",children:a?r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"flex-shrink-0",children:r.jsx("div",{className:"p-2 bg-green-100 dark:bg-green-900 rounded-full",children:r.jsx("svg",{className:"h-6 w-6 text-green-500 dark:text-green-400",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"})})})}),r.jsxs("div",{children:[r.jsx("p",{className:"text-sm font-medium text-gray-900 dark:text-white",children:"Price drop alert sent!"}),r.jsx("p",{className:"text-sm text-gray-500 dark:text-gray-400",children:"Check your email for details."})]})]}):r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"flex-shrink-0",children:r.jsx("div",{className:"p-2 bg-blue-100 dark:bg-blue-900 rounded-full",children:r.jsx("svg",{className:"h-6 w-6 text-blue-500 dark:text-blue-400",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"})})})}),r.jsxs("div",{children:[r.jsxs("p",{className:"text-sm font-medium text-gray-900 dark:text-white",children:["Alert scheduled for ₹",e==null?void 0:e.toLocaleString()]}),r.jsxs("p",{className:"text-sm text-gray-500 dark:text-gray-400",children:["You'll be notified at ",t]})]})]})})}),mt=()=>r.jsx("footer",{className:"bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800",children:r.jsx("div",{className:"container mx-auto px-4 py-8",children:r.jsxs("div",{className:"flex flex-col md:flex-row justify-between items-center",children:[r.jsxs("div",{className:"text-sm text-gray-500 dark:text-gray-400",children:["© ",new Date().getFullYear()," PricePulse. All rights reserved."]}),r.jsxs("nav",{className:"flex space-x-6 mt-4 md:mt-0",children:[r.jsx("a",{href:"#",className:"text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white",children:"About"}),r.jsx("a",{href:"#",className:"text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white",children:"GitHub"}),r.jsx("a",{href:"#",className:"text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white",children:"Contact"}),r.jsx("a",{href:"#",className:"text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white",children:"Privacy Policy"})]})]})})});class pt extends B.Component{constructor(t){super(t),this.state={hasError:!1,error:null}}static getDerivedStateFromError(t){return{hasError:!0,error:t}}componentDidCatch(t,a){console.error("Error caught by boundary:",t,a)}render(){var t;return this.state.hasError?r.jsx("div",{className:"min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4",children:r.jsx("div",{className:"max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",children:r.jsxs("div",{className:"text-center",children:[r.jsx("svg",{className:"mx-auto h-12 w-12 text-red-500",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"})}),r.jsx("h2",{className:"mt-4 text-lg font-semibold text-gray-900 dark:text-white",children:"Something went wrong"}),r.jsx("p",{className:"mt-2 text-sm text-gray-600 dark:text-gray-400",children:((t=this.state.error)==null?void 0:t.message)||"An unexpected error occurred"}),r.jsx("button",{onClick:()=>window.location.reload(),className:"mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",children:"Refresh Page"})]})})}):this.props.children}}const T="http://localhost:5000/api";function gt(){const[e,t]=d.useState(null),[a,o]=d.useState(null),[i,s]=d.useState(!1),[l,n]=d.useState(null),[u,m]=d.useState(!1);d.useEffect(()=>{const g=localStorage.getItem("productData");if(g)try{const x=JSON.parse(g);t(x),h(x.url)}catch(x){console.error("Error loading saved product data:",x),localStorage.removeItem("productData")}},[]);const c=async g=>{try{s(!0),n(null);const x=await fetch(`${T}/api/track`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(g)});if(!x.ok){const O=await x.json();throw new Error(O.message||"Failed to start tracking product")}const R=await x.json();t(g),o(R),localStorage.setItem("productData",JSON.stringify(g))}catch(x){throw n(x instanceof Error?x.message:"An error occurred"),x}finally{s(!1)}},h=async g=>{try{m(!0),n(null);const x=await fetch(`${T}/api/refresh/${encodeURIComponent(g)}`);if(!x.ok){const O=await x.json();throw new Error(O.message||"Failed to refresh data")}const R=await x.json();o(R)}catch(x){n(x instanceof Error?x.message:"An error occurred")}finally{m(!1)}},p=()=>{t(null),o(null),localStorage.removeItem("productData")};return r.jsx(pt,{children:r.jsx(Z,{children:r.jsxs("div",{className:"min-h-screen bg-gray-50 dark:bg-gray-900",children:[r.jsx(it,{}),r.jsxs("main",{className:"container mx-auto px-4 py-8 space-y-8",children:[!a&&r.jsx(nt,{onSubmit:c}),i&&!a&&r.jsx("div",{className:"flex justify-center items-center py-12",children:r.jsx(M,{size:"lg",text:"Loading product data..."})}),l&&r.jsx("div",{className:"bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-600 dark:text-red-400",children:r.jsxs("div",{className:"flex items-center",children:[r.jsx("svg",{className:"h-5 w-5 mr-2",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:r.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:2,d:"M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"})}),l]})}),a&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"flex justify-end",children:r.jsx("button",{onClick:p,className:"text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300",children:"Clear Data"})}),r.jsx(lt,{image:a.image,title:a.title,currentPrice:a.currentPrice,amazonUrl:a.amazonUrl,status:a.status}),r.jsxs("div",{className:"relative",children:[u&&r.jsx("div",{className:"absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-10",children:r.jsx(M,{size:"md",text:"Refreshing data..."})}),r.jsx(dt,{data:a.priceHistory,onRefresh:()=>(e==null?void 0:e.url)&&h(e.url)})]}),r.jsx(ct,{prices:a.platformPrices}),r.jsx(ut,{targetPrice:e==null?void 0:e.targetPrice,email:e==null?void 0:e.email,isPriceDrop:a.status==="price_drop"})]})]}),r.jsx(mt,{}),r.jsx(tt,{position:"bottom-right",toastOptions:{duration:4e3,style:{background:"#333",color:"#fff"}}})]})})})}A.createRoot(document.getElementById("root")).render(r.jsx(B.StrictMode,{children:r.jsx(gt,{})}));
//# sourceMappingURL=index-Bg3-L4zC.js.map
