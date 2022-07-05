"use strict";(self.webpackChunkpiperider_report=self.webpackChunkpiperider_report||[]).push([[870],{4870:function(e,n,t){t.r(n),t.d(n,{default:function(){return v}});var i=t(841),r=t(3777),s=t(623),a=t(9596),l=t(7313),c=t(6629),d=t(1382),o=t(2954),u=t(5847),x=t(8511),h=t(2207);var j=t(4033),m=t(6417),f=function(e){var n=e.column,t=(0,o.gQ)(n),r=t.mismatch,s=t.mismatchOfTotal,a=t.missing,l=t.valid,c=t.validOfTotal;return(0,m.jsxs)(i.kC,{direction:"column",gap:3,children:[(0,m.jsxs)(i.xv,{maxWidth:"100%",children:[(0,m.jsx)(i.xv,{as:"span",fontWeight:700,color:"gray.900",fontSize:"lg",mr:1,title:n.name,noOfLines:1,children:n.name}),"","(",(0,m.jsx)(i.EK,{children:n.schema_type}),")"]}),(0,m.jsx)(i.kC,{direction:"column",children:(0,m.jsx)(j.$,{name:"Total",base:(0,o.uf)(n.total)})}),(0,m.jsxs)(i.kC,{direction:"column",mt:3,children:[(0,m.jsx)(j.$,{name:"Valid",base:l,input:(0,o.uf)(c,"en-US",{style:"percent"})}),(0,m.jsx)(j.$,{name:"Mismatched",base:r,input:(0,o.uf)(s,"en-US",{style:"percent"})}),(0,m.jsx)(j.$,{name:"Missing",base:a,input:(0,o.ro)(n)})]}),(0,m.jsx)(i.kC,{direction:"column",mt:3,children:(0,m.jsx)(j.$,{name:"Distinct",base:(0,o.uf)(n.distinct)})}),"string"===n.type&&(0,m.jsx)(i.kC,{direction:"column",children:(0,m.jsx)(j.$,{name:"Most common",base:(0,o.jg)(n),baseWidth:"200px"})}),"numeric"===n.type&&(0,m.jsxs)(i.kC,{direction:"column",children:[(0,m.jsx)(j.$,{name:"Min",base:(0,o.uf)(n.min)}),(0,m.jsx)(j.$,{name:"Max",base:(0,o.uf)(n.max)}),(0,m.jsx)(j.$,{name:"Avg",base:(0,o.uf)(n.avg)})]}),"datetime"===n.type&&(0,m.jsxs)(i.kC,{direction:"column",children:[(0,m.jsx)(j.$,{name:"Min",base:n.min}),(0,m.jsx)(j.$,{name:"Max",base:n.max})]})]})};function v(e){var n=e.data,t=e.name,a=n.datasource,l=n.tables[t];if((0,u.j)(t),!n)return(0,m.jsx)(d.o,{children:(0,m.jsx)(i.kC,{justifyContent:"center",alignItems:"center",minHeight:"100vh",children:"No profile data found."})});var x=(0,o.c6)(null!==l&&void 0!==l&&l.assertion_results?l.assertion_results:void 0);return(0,m.jsx)(d.o,{children:(0,m.jsxs)(i.kC,{direction:"column",minH:"calc(100vh + 1px)",width:"100%",children:[(0,m.jsx)(i.kC,{mx:"10%",mt:4,children:(0,m.jsxs)(r.aG,{fontSize:"lg",children:[(0,m.jsx)(r.gN,{children:(0,m.jsx)(c.rU,{href:"/",children:(0,m.jsx)(r.At,{href:"/",children:a.name})})}),(0,m.jsx)(r.gN,{isCurrentPage:!0,children:(0,m.jsx)(r.At,{href:"#",children:l.name})})]})}),(0,m.jsxs)(i.kC,{border:"1px solid",borderColor:"gray.300",bg:"white",borderRadius:"md",p:6,mt:3,mx:"10%",direction:"column",children:[(0,m.jsxs)(i.kC,{direction:"column",gap:4,mb:8,children:[(0,m.jsx)(i.X6,{size:"lg",children:"Overview"}),(0,m.jsxs)(i.xv,{children:["Table:"," ",(0,m.jsx)(i.xv,{as:"span",fontWeight:700,children:l.name})]}),(0,m.jsxs)(i.xv,{children:["Rows:"," ",(0,m.jsx)(i.xv,{as:"span",fontWeight:700,children:(0,o.uf)(l.row_count)})]}),(0,m.jsxs)(i.xv,{children:["Columns:"," ",(0,m.jsx)(i.xv,{as:"span",fontWeight:700,children:(0,o.uf)(l.col_count)})]}),(0,m.jsxs)(i.xv,{children:["Test Status:"," ",(0,m.jsx)(i.xv,{as:"span",fontWeight:700,children:x.passed})," ","Passed,"," ",(0,m.jsx)(i.xv,{as:"span",fontWeight:700,color:x.failed>0?"red.500":"inherit",children:x.failed})," ","Failed"]})]}),(0,m.jsxs)(s.mQ,{isLazy:!0,children:[(0,m.jsxs)(s.td,{children:[(0,m.jsx)(s.OK,{children:"Profiling"}),(0,m.jsx)(s.OK,{children:"Tests"}),l.dbt_test_results&&(0,m.jsx)(s.OK,{children:"dbt Tests"})]}),(0,m.jsxs)(s.nP,{children:[(0,m.jsx)(s.x4,{children:(0,m.jsx)(p,{data:l.columns})}),(0,m.jsx)(s.x4,{children:(0,m.jsx)(g,{data:l.assertion_results})}),(null===l||void 0===l?void 0:l.dbt_test_results)&&(0,m.jsx)(s.x4,{children:(0,m.jsx)(g,{type:"dbt",data:l.dbt_test_results})})]})]})]})]})})}function p(e){var n=e.data;return(0,m.jsx)(i.kC,{direction:"column",gap:4,children:Object.keys(n).map((function(e){var t=n[e],r=t.distribution;return(0,m.jsxs)(i.kC,{direction:"column",px:4,children:[(0,m.jsxs)(i.rj,{my:4,templateColumns:"minmax(270px, 1fr) 1fr",gap:12,children:[(0,m.jsx)(f,{column:t}),(0,m.jsx)(i.kC,{mt:8,justifyContent:"center",alignItems:"center",children:r?(0,m.jsx)(b,{data:r.labels.map((function(e,n){return{label:e,value:r.counts[n],total:t.total}}))}):(0,m.jsx)(i.xv,{children:"No data available"})})]}),(0,m.jsx)(i.iz,{my:4})]},e)}))})}function g(e){var n=e.data,t=e.type,r=void 0===t?"piperider":t,s=null===n||void 0===n?void 0:n.tests,l=null===n||void 0===n?void 0:n.columns;return 0===s.length&&0===Object.keys(l).length?(0,m.jsx)(i.kC,{direction:"column",children:(0,m.jsx)(i.xv,{textAlign:"center",children:"No tests available"})}):(0,m.jsx)(i.kC,{direction:"column",gap:4,children:(0,m.jsx)(a.xJ,{children:(0,m.jsxs)(a.iA,{variant:"simple",children:[(0,m.jsx)(a.hr,{children:(0,m.jsxs)(a.Tr,{children:[(0,m.jsx)(a.Th,{children:"Level"}),(0,m.jsx)(a.Th,{children:"Column"}),(0,m.jsx)(a.Th,{children:"Assertion"}),(0,m.jsx)(a.Th,{children:"Status"}),"piperider"===r&&(0,m.jsx)(a.Th,{children:"Expected"}),"piperider"===r&&(0,m.jsx)(a.Th,{children:"Actual"}),"dbt"===r&&(0,m.jsx)(a.Th,{children:"Messagae"})]})}),(0,m.jsxs)(a.p3,{children:[s.map((function(e){var n,t="failed"===e.status;return(0,m.jsxs)(a.Tr,{children:[(0,m.jsx)(a.Td,{children:"Table"}),(0,m.jsx)(a.Td,{children:"-"}),(0,m.jsx)(a.Td,{children:e.name}),(0,m.jsx)(a.Td,{children:t?(0,m.jsx)(i.xv,{as:"span",role:"img",children:"\u274c"}):(0,m.jsx)(i.xv,{as:"span",role:"img",children:"\u2705"})}),"piperider"===r&&(0,m.jsx)(a.Td,{children:(0,o.aH)(e.expected)}),"piperider"===r&&(0,m.jsx)(a.Td,{color:t?"red.500":"inherit",children:(0,o.aH)(e.actual)}),"dbt"===r&&(0,m.jsx)(a.Td,{children:null!==(n=e.message)&&void 0!==n?n:"-"})]},e.name)})),Object.keys(l).map((function(e){return l[e].map((function(n){var t,s="failed"===n.status;return(0,m.jsxs)(a.Tr,{children:[(0,m.jsx)(a.Td,{children:"Column"}),(0,m.jsx)(a.Td,{children:e}),(0,m.jsx)(a.Td,{children:n.name}),(0,m.jsx)(a.Td,{children:s?(0,m.jsx)(i.xv,{as:"span",role:"img",children:"\u274c"}):(0,m.jsx)(i.xv,{as:"span",role:"img",children:"\u2705"})}),"piperider"===r&&(0,m.jsx)(a.Td,{children:(0,o.aH)(n.expected)}),"piperider"===r&&(0,m.jsx)(a.Td,{color:s?"red.500":"inherit",children:(0,o.aH)(n.actual)}),"dbt"===r&&(0,m.jsx)(a.Td,{children:null!==(t=n.message)&&void 0!==t?t:"-"})]},n.name)}))}))]})]})})})}function b(e){var n=e.data,t=(0,l.useRef)(null),r=(0,l.useRef)(null);return function(e){var n=e.target,t=e.data,i=e.dimensions;(0,l.useEffect)((function(){if(n&&i&&t){var e=h.Ys(n.current),r=h.tiA().domain(t.map((function(e){return e.label}))).range([0,i.width]).padding(.05),s=h.LLu(r).tickFormat((function(e,n){var t=r.domain().length-1;return 0===n||n===t/2||n===t?e:null}));e.select(".x-axis").style("transform","translateY(".concat(i.height,"px)")).call(s);var a=h.BYU().domain([0,h.Fp7(t,(function(e){return e.value}))]).range([i.height,0]),l=h.y4O(a);e.select(".y-axis").call(l),e.selectAll(".bar").data(t).join("rect").attr("class","bar").attr("x",(function(e){return r(e.label)})).attr("y",(function(e){return a(e.value)})).attr("width",r.bandwidth()).attr("height",(function(e){return i.height-a(e.value)})).style("fill","var(--chakra-colors-blue-300)");var c=(0,o.vy)({target:".chart"});return e.selectAll(".overlay-bars").data(t).join("rect").attr("class","overlay-bars").attr("x",(function(e){return r(e.label)})).attr("y",(function(){return 0})).attr("width",r.bandwidth()).attr("height",(function(){return i.height})).style("opacity",0).on("mouseover",(function(e,n){var t=n,i=t.label,r=t.value,s=t.total;c.html("\n          <div>\n            <p>Label: ".concat(i,"</p>\n            <p>Count: ").concat((0,o.uf)(r),"</p>\n            <p>Percentage: ").concat(Number(r/s*100).toFixed(3),"%</p>\n          </div>\n        ")).transition().duration(500).style("visibility","visible"),h.Ys(this).style("fill","var(--chakra-colors-gray-500)").style("opacity",.3)})).on("mousemove",(function(e){c.style("top","".concat(e.pageY-10,"px")).style("left","".concat(e.pageX+10,"px"))})).on("mouseout",(function(){c.html("").transition().duration(500).style("visibility","hidden"),h.Ys(this).style("opacity",0)})),function(){e.select("svg").remove()}}}),[n,i,t])}({target:t,data:n,dimensions:(0,x.y)(r)}),(0,m.jsx)(i.kC,{className:"chart",width:"100%",ref:r,children:(0,m.jsxs)("svg",{width:"100%",overflow:"visible",ref:t,children:[(0,m.jsx)("g",{className:"x-axis"}),(0,m.jsx)("g",{className:"y-axis"})]})})}},4033:function(e,n,t){t.d(n,{$:function(){return s}});var i=t(841),r=t(6417);function s(e){var n=e.name,t=e.base,s=e.input,a=void 0===s?null:s,l=e.baseWidth,c=void 0===l?"100px":l,d=e.inputWidth,o=void 0===d?"100px":d;return(0,r.jsxs)(i.kC,{justifyContent:"space-between",children:[(0,r.jsx)(i.xv,{fontWeight:700,children:n}),(0,r.jsxs)(i.kC,{gap:{lg:5,md:1},children:[(0,r.jsx)(i.xv,{textAlign:"right",width:c,noOfLines:1,children:t}),a&&(0,r.jsx)(i.xv,{textAlign:"right",width:o,children:a})]})]})}},8511:function(e,n,t){t.d(n,{y:function(){return s}});var i=t(885),r=t(7313);function s(e){var n=(0,r.useState)(null),t=(0,i.Z)(n,2),s=t[0],a=t[1];return(0,r.useEffect)((function(){if(e&&e.current){var n=e.current,t=new ResizeObserver((function(e){e.forEach((function(e){a(e.contentRect)}))}));return t.observe(n),function(){t.unobserve(n)}}}),[e]),s}}}]);