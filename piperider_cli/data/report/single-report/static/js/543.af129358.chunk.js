"use strict";(self.webpackChunkpiperider_report=self.webpackChunkpiperider_report||[]).push([[543],{3597:function(e,n,t){t.d(n,{f:function(){return c}});var r=t(8735),i=t(2791),a=t(8453),l=t(9227),s=t(1971),o=t(9842);var u=t(184);function c(e){var n=e.data,t=(0,i.useRef)(null),c=(0,i.useRef)(null);return function(e){var n=e.target,t=e.data,r=e.dimensions;(0,i.useEffect)((function(){if(n&&r&&t){var e=l.Ys(n.current),i=l.tiA().domain(t.map((function(e){return String(e.label)}))).range([0,r.width]).padding(.05),a=l.LLu(i).tickFormat((function(e,n){var t=i.domain().length-1;return 0===n||n===t/2||n===t?e:null}));e.select(".x-axis").style("transform","translateY(".concat(r.height,"px)")).call(a);var u=l.BYU().domain([0,l.Fp7(t,(function(e){return e.value}))]).range([r.height,0]),c=l.y4O(u);e.select(".y-axis").call(c),e.selectAll(".bar").data(t).join("rect").attr("class","bar").attr("x",(function(e){return i(e.label)})).attr("y",(function(e){return u(e.value)})).attr("width",i.bandwidth()).attr("height",(function(e){return r.height-u(e.value)})).style("fill","var(--chakra-colors-blue-300)");var d=(0,o.v)({target:".chart"});return e.selectAll(".overlay-bars").data(t).join("rect").attr("class","overlay-bars").attr("x",(function(e){return i(String(e.label))})).attr("y",(function(){return 0})).attr("width",i.bandwidth()).attr("height",(function(){return r.height})).style("opacity",0).on("mouseover",(function(e,n){var t=n.label,r=n.value,i=n.total,a=(0,o.p)(n);d.html("\n          <div>\n            <p>".concat(a,": ").concat(t,"</p>\n            <p>Count: ").concat((0,s.uf)(r),"</p>\n            <p>Percentage: ").concat(Number(r/i*100).toFixed(3),"%</p>\n          </div>\n        ")).transition().duration(500).style("visibility","visible"),l.Ys(this).style("fill","var(--chakra-colors-gray-500)").style("opacity",.3)})).on("mousemove",(function(e){d.style("top","".concat(e.pageY-10,"px")).style("left","".concat(e.pageX+10,"px"))})).on("mouseout",(function(){d.html("").transition().duration(500).style("visibility","hidden"),l.Ys(this).style("opacity",0)})),function(){e.select("svg").remove(),e.selectAll(".chart_tooltip").remove()}}}),[n,r,t])}({target:t,data:n,dimensions:(0,a.y)(c)}),(0,u.jsx)(r.kC,{className:"chart",width:"100%",minHeight:230,ref:c,children:(0,u.jsxs)("svg",{width:"100%",overflow:"visible",ref:t,children:[(0,u.jsx)("g",{className:"x-axis"}),(0,u.jsx)("g",{className:"y-axis"})]})})}},543:function(e,n,t){t.r(n),t.d(n,{default:function(){return te}});var r=t(8735),i=t(6837),a=t(4385),l=t(8625),s=t(7260),o=t(2483),u=t(6786),c=t(3442),d=t(6523),h=t(922),v=t(3597),x=t(184),m=function(e){var n=e.children;return(0,x.jsx)(r.kC,{p:2,bg:"white",height:"inherit",maxHeight:330,overflowY:"auto",direction:"column",borderBottomRadius:"inherit",children:n})},f=t(5223),p=t(1564),j=t(2504),g=function(e){var n=e.title,t=e.children,i=e.allowModalPopup,a=(0,f.qY)(),l=a.onOpen,s=a.isOpen,o=a.onClose;return(0,x.jsxs)(x.Fragment,{children:[(0,x.jsx)(r.kC,{px:12,py:9,my:3,mx:3,maxHeight:"300px",bg:"whiteAlpha.700",rounded:"md",onClick:function(){return i&&l()},children:t}),(0,x.jsxs)(p.u_,{size:"4xl",isOpen:s,onClose:o,children:[(0,x.jsx)(p.ZA,{}),(0,x.jsxs)(p.hz,{p:12,children:[(0,x.jsx)(p.xB,{children:n}),(0,x.jsx)(p.ol,{}),(0,x.jsx)(p.fe,{children:t}),(0,x.jsx)(p.mz,{children:(0,x.jsx)(r.kC,{mt:6,w:"100%",direction:"row",justify:"center",children:(0,x.jsx)(j.zx,{colorScheme:"blue",mr:3,onClick:o,children:"Close"})})})]})]})]})},b=t(2220),y=t(9113),T=t(5272),k=t(8820),C=t(7692),z=t(9126),w=t(4651),D=t(1578),_=t(6036),O=t(1971),A=t(972);function K(e){var n=e.columnDatum,t=n.description,i=n.name,a=n.schema_type,l=function(e){var n=e.type,t=(0,h.JH)(e);if(t&&"string"===n)return{backgroundColor:"purple.500",icon:D.Vmi};if(t&&"integer"===n)return{backgroundColor:"orange.500",icon:_.RAZ};if("string"===n)return{backgroundColor:"blue.500",icon:C.sXe};if("numeric"===n||"integer"===n)return{backgroundColor:"red.500",icon:w.Wrf};if("datetime"===n)return{backgroundColor:"teal.500",icon:z.KvO};if("boolean"===n)return{backgroundColor:"pink.500",icon:D.OG8};if("other"===n)return{backgroundColor:"limegreen",icon:k.wEQ};return{backgroundColor:"gray.500",icon:C.cpG}}(n),s=l.backgroundColor,o=l.icon;return(0,x.jsxs)(r.kC,{p:2,bg:"white",justify:"space-between",alignItems:"center",width:"100%",borderTopRadius:"inherit",children:[(0,x.jsxs)(r.kC,{alignItems:"center",children:[(0,x.jsx)(b.u,{label:a,shouldWrapChildren:!0,children:(0,x.jsx)(y.JO,{mt:1,mx:2,p:1,rounded:"md",color:"white",backgroundColor:s,as:o,boxSize:7})}),(0,x.jsx)(r.xv,{fontWeight:"semibold",fontSize:"3xl",children:(0,O.o2)(i,10)})]}),(0,x.jsx)(A.l,{label:t,prefix:" - via ",children:(0,x.jsx)(T.sz,{color:"gray.400",boxSize:"20px",mr:3})})]})}var P={total:"The total count of values, regardless validity",nulls:"The count of values that are null type",non_nulls:"The count of non null values",distinct:"The count of distinct kinds of values (e.g. [a,b,c,c] => [a,b,c])",duplicates:"The count of values that are recurring (e.g. [a,b,c,c] => [c,c])",non_duplicates:"The count of values that are non-recurring (e.g. [a,b,c,c] => [a,b])",topk:"The most common or frequent value",name:"Name of this column",description:"Descriptor of this column",type:"Generic types of schema, python-based",schema_type:"The column type definition in SQL database",valids:"The count of values that are non-null and not invalid",invalids:"The count of values that don't match the schema type. For example, a string in a numeric column.",zeros:"The count of numerical values that equal zero exactly",negatives:"The count of numerical values that are less than zero",positives:"The count of numerical values that are more than zero",zero_length:"The count of string values with zero lengths exactly",non_zero_length:"The count of string values with non-zero lengths",trues:"The count of boolean true values",falses:"The count of boolean false values",sum:"The sum of a column's values",avg:"The average of a column's values",stddev:"The standard deviation of a column's values",min:"The minimum value of a column's range",max:"The maximum value of a columns's range",p5:"The quantile value of the dataset (5th percentile)",p25:"The quantile value of the dataset (25th percentile)",p50:"The quantile value of the dataset (50th percentile)",p75:"The quantile value of the dataset (75th percentile)",p95:"The quantile value of the dataset (95th percentile)"},E=function(e){var n=e.label,t=e.value,i=e.subvalue,a=e.metaKey,l="string"===typeof a?P[a]:null;return(0,x.jsxs)(r.kC,{direction:"column",w:"100%",mx:2,my:2,children:[(0,x.jsx)(b.u,{label:l,isDisabled:!Boolean(l),placement:"top",children:(0,x.jsxs)(r.kC,{alignItems:"center",w:"fit-content",children:[(0,x.jsx)(r.xv,{lineHeight:"5",fontSize:"small",children:n}),(0,x.jsx)(T.sz,{color:"gray.400",boxSize:"12px",ml:2})]})}),(0,x.jsx)(r.xv,{fontWeight:"bold",children:t}),i&&(0,x.jsx)(r.xv,{fontSize:"smaller",children:i})]})},S=t(2387);function W(e){var n=e.columnDatum,t=e.children,i=n.nulls,a=n.invalids,l=(0,h.gQ)(n),s=l.invalidsOfTotal,o=l.nullsOfTotal;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsx)(r.xv,{textAlign:"center",fontWeight:"bold",my:2,children:"Data Composition"}),(0,x.jsx)(r.iz,{}),(0,x.jsxs)(r.kC,{justify:"space-evenly",children:[(0,x.jsx)(E,{metaKey:"nulls",label:S.td,value:(0,O.uy)(o,O.Zn),subvalue:i}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"invalids",label:S.ST,value:(0,O.uy)(s,O.Zn),subvalue:a}),t]})]})}var N=function(e){var n=e.columnDatum,t=n.trues,i=n.falses;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(W,{columnDatum:n,children:[(0,x.jsx)(E,{label:S.aJ,value:(0,O.uy)(i,O.uf),metaKey:"falses"}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{label:S.Y0,value:(0,O.uy)(t,O.uf),metaKey:"trues"})]}),(0,x.jsx)(r.iz,{})]})};function Z(e){var n=e.columnDatum,t=n.distinct,i=n.duplicates,a=(0,h.gQ)(n),l=a.distinctOfTotal,s=a.duplicatesOfTotal;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsx)(r.xv,{textAlign:"center",fontWeight:"bold",my:2,children:"Uniqueness"}),(0,x.jsx)(r.iz,{}),(0,x.jsxs)(r.kC,{justify:"space-evenly",children:[(0,x.jsx)(E,{metaKey:"distinct",label:S.A$,value:(0,O.uy)(l,O.Zn),subvalue:t}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"duplicates",label:S.hD,value:(0,O.uy)(s,O.Zn),subvalue:i})]})]})}var G=function(e){var n=e.columnDatum,t=(0,h.gQ)(n).validsOfTotal,i=n.valids,a=(0,O.Th)(n),l=a.topValues,s=a.topCounts;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(W,{columnDatum:n,children:[(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"valids",label:S.Px,value:(0,O.uy)(t,O.Zn),subvalue:i})]}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(Z,{columnDatum:n}),(0,x.jsx)(r.iz,{}),l&&s&&(0,x.jsx)(E,{metaKey:"topk",label:S.IK,value:l,subvalue:s})]})};function I(e){var n=e.columnDatum,t=n.avg,i=n.stddev,a=n.min,l=n.max,s="string"===n.type,o=(0,h.JH)(n),u=s&&!o?"Length":"Data";return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(r.xv,{textAlign:"center",fontWeight:"bold",my:2,children:[u," Statistics"]}),(0,x.jsx)(r.iz,{}),t&&(0,x.jsxs)(r.kC,{justify:"space-evenly",children:[(0,x.jsx)(E,{metaKey:"avg",label:S.dc,value:(0,O.uy)(t,O.uf)}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"stddev",label:S.lb,value:S.o6+(0,O.uy)(i,O.uf)}),(0,x.jsx)(r.iz,{orientation:"vertical"})]}),(0,x.jsx)(r.iz,{}),(0,x.jsxs)(r.kC,{justify:"space-evenly",children:[(0,x.jsx)(E,{metaKey:"min",label:S.KX,value:(0,O.uy)(a,O.uf)}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"max",label:S.k2,value:(0,O.uy)(l,O.uf)})]})]})}var R=function(e){var n=e.columnDatum;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsx)(W,{columnDatum:n}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(Z,{columnDatum:n}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(I,{columnDatum:n})]})},L=t(7005),Y=t(5984);function q(e){var n=e.columnDatum;d.a$.parse(n);var t=[{label:"Min",value:n.min,metaKey:"min"},{label:"5%",value:n.p5,metaKey:"p5"},{label:"25%",value:n.p25,metaKey:"p25"},{label:"50%",value:n.p50,metaKey:"p50"},{label:"75%",value:n.p75,metaKey:"p75"},{label:"95%",value:n.p95,metaKey:"p95"},{label:"Max",value:n.max,metaKey:"max"}];return(0,x.jsx)(L.xJ,{w:"100%",children:(0,x.jsxs)(L.iA,{size:"sm",variant:"simple",children:[(0,x.jsx)(L.hr,{children:(0,x.jsx)(L.Tr,{children:t.map((function(e){return(0,x.jsx)(L.Th,{pr:0,pl:2,textAlign:"center",children:(0,x.jsx)(b.u,{label:P[e.metaKey],children:e.label})},(0,Y.x0)())}))})}),(0,x.jsx)(L.p3,{children:(0,x.jsx)(L.Tr,{children:t.map((function(e){return(0,x.jsx)(L.Td,{pr:0,pl:2,textAlign:"center",children:(0,O.uy)(e.value,O.J8)},(0,Y.x0)())}))})})]})})}var H=function(e){var n=e.columnDatum,t=n.negatives,i=n.zeros,a=(0,h.gQ)(n),l=a.negativesOfTotal,s=a.zerosOfTotal;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(W,{columnDatum:n,children:[(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"negatives",label:S.wC,value:(0,O.uy)(l,O.Zn),subvalue:t}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"zeros",label:S.AG,value:(0,O.uy)(s,O.Zn),subvalue:i})]}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(I,{columnDatum:n}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(r.kC,{mt:2,children:(0,x.jsx)(q,{columnDatum:n})})]})},Q=function(e){var n=e.columnDatum,t=n.valids,i=(0,h.gQ)(n).validsOfTotal;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(W,{columnDatum:n,children:[(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"valids",label:S.Px,value:(0,O.uy)(i,O.Zn),subvalue:t})]}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(Z,{columnDatum:n}),(0,x.jsx)(r.iz,{})]})},J=function(e){var n=e.columnDatum,t=n.zero_length,i=(0,h.gQ)(n).zeroLengthOfTotal;return(0,x.jsxs)(r.kC,{direction:"column",children:[(0,x.jsxs)(W,{columnDatum:n,children:[(0,x.jsx)(r.iz,{orientation:"vertical"}),(0,x.jsx)(E,{metaKey:"zero_length",label:S.cU,value:(0,O.uy)(i,O.Zn),subvalue:t})]}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(Z,{columnDatum:n}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(I,{columnDatum:n}),(0,x.jsx)(r.iz,{}),(0,x.jsx)(r.kC,{justify:"space-evenly"})]})};function F(e){var n=e.columnDatum;d.a$.parse(n);var t=n.name;return(0,x.jsxs)(r.kC,{direction:"column",bg:"gray.300",width:{xl:"32%",lg:"45%",md:"100%",base:"100%"},border:"1px solid",borderColor:"gray.300",h:[700],my:3,rounded:"lg",overflowX:"hidden",children:[(0,x.jsx)(K,{columnDatum:n}),(0,x.jsx)(g,{title:t,allowModalPopup:Boolean((0,h.cc)(n)),children:V(n)}),(0,x.jsx)(m,{children:B(n)})]})}function V(e){var n=(0,h.cc)(e);return n?(0,x.jsx)(v.f,{data:n}):(0,x.jsx)(r.kC,{h:230,alignItems:"center",w:"100%",children:(0,x.jsx)(r.xv,{textAlign:"center",w:"inherit",children:"No data available"})})}function B(e){var n=e.type,t=(0,h.JH)(e);return"string"!==n&&"integer"!==n||!t?"numeric"===n||"integer"===n?(0,x.jsx)(H,{columnDatum:e}):"boolean"===n?(0,x.jsx)(N,{columnDatum:e}):"string"===n?(0,x.jsx)(J,{columnDatum:e}):"datetime"===n?(0,x.jsx)(R,{columnDatum:e}):"other"===n?(0,x.jsx)(Q,{columnDatum:e}):(0,x.jsxs)(r.xv,{textAlign:"center",w:"inherit",children:["The column type: ",n," cannot be displayed"]}):(0,x.jsx)(G,{columnDatum:e})}function M(e){var n=e.data;return(0,x.jsx)(r.kC,{direction:"row",flexWrap:"wrap",gap:4,children:Object.keys(n).map((function(e){var t=n[e];return(0,d.h5)(d.a$.safeParse(t)),(0,x.jsx)(F,{columnDatum:t},(0,Y.x0)())}))})}var U=t(4821),X=t(874);function $(e){var n=e.assertionData,t=e.type,i=void 0===t?"piperider":t,a=null===n||void 0===n?void 0:n.tests,l=(null===n||void 0===n?void 0:n.columns)||{};return!a||0===a.length&&0===Object.keys(l).length?(0,x.jsx)(r.kC,{direction:"column",children:(0,x.jsx)(r.xv,{textAlign:"center",children:"No tests available"})}):(0,x.jsx)(r.kC,{direction:"column",gap:4,children:(0,x.jsx)(L.xJ,{children:(0,x.jsxs)(L.iA,{variant:"simple",children:[(0,x.jsx)(L.hr,{children:(0,x.jsxs)(L.Tr,{children:[(0,x.jsx)(L.Th,{children:"Level"}),(0,x.jsx)(L.Th,{children:"Column"}),(0,x.jsx)(L.Th,{children:"Assertion"}),(0,x.jsx)(L.Th,{children:"Status"}),"piperider"===i&&(0,x.jsx)(L.Th,{children:"Expected"}),"piperider"===i&&(0,x.jsx)(L.Th,{children:"Actual"})]})}),(0,x.jsxs)(L.p3,{children:[a.map((function(e){(0,d.h5)(U.S1.safeParse(e));var n="failed"===e.status;return(0,x.jsxs)(L.Tr,{children:[(0,x.jsx)(L.Td,{children:"Table"}),(0,x.jsx)(L.Td,{children:"-"}),(0,x.jsx)(L.Td,{children:e.name}),(0,x.jsx)(L.Td,{children:n?(0,x.jsx)(r.xv,{as:"span",role:"img",children:"\u274c"}):(0,x.jsx)(r.xv,{as:"span",role:"img",children:"\u2705"})}),"piperider"===i&&(0,x.jsx)(L.Td,{children:(0,O.sG)(e.expected)}),"piperider"===i&&(0,x.jsx)(L.Td,{color:n?"red.500":"inherit",children:(0,O.sG)(e.actual)})]},e.name)})),Object.keys(l).map((function(e){var n=l[e];return(0,d.h5)(X.z.array(U.S1).safeParse(n)),n.map((function(n){var t="failed"===n.status;return(0,x.jsxs)(L.Tr,{children:[(0,x.jsx)(L.Td,{children:"Column"}),(0,x.jsx)(L.Td,{children:e}),(0,x.jsx)(L.Td,{children:n.name}),(0,x.jsx)(L.Td,{children:t?(0,x.jsx)(r.xv,{as:"span",role:"img",children:"\u274c"}):(0,x.jsx)(r.xv,{as:"span",role:"img",children:"\u2705"})}),"piperider"===i&&(0,x.jsx)(L.Td,{children:(0,O.sG)(n.expected)}),"piperider"===i&&(0,x.jsx)(L.Td,{color:t?"red.500":"inherit",children:(0,O.sG)(n.actual)})]},n.name)}))}))]})]})})})}var ee=t(6157);function ne(e){var n=e.table;(0,d.h5)(d.vT.safeParse(n));var t=(0,ee.YI)(n.piperider_assertion_result,n.dbt_assertion_result);return(0,x.jsxs)(r.kC,{direction:"column",gap:4,mb:8,children:[(0,x.jsx)(r.X6,{size:"lg",children:"Overview"}),(0,x.jsxs)(r.xv,{children:["Table:"," ",(0,x.jsx)(r.xv,{as:"span",fontWeight:700,children:n.name})]}),(0,x.jsxs)(r.xv,{children:["Rows:"," ",(0,x.jsx)(r.xv,{as:"span",fontWeight:700,children:(0,O.uy)(n.row_count,O.uf)})]}),(0,x.jsxs)(r.xv,{children:["Columns:"," ",(0,x.jsx)(r.xv,{as:"span",fontWeight:700,children:(0,O.uy)(n.col_count,O.uf)})]}),(0,x.jsxs)(r.xv,{children:["Test Status:"," ",(0,x.jsx)(r.xv,{as:"span",fontWeight:700,children:t.passed})," ","Passed,"," ",(0,x.jsx)(r.xv,{as:"span",fontWeight:700,color:t.failed>0?"red.500":"inherit",children:t.failed})," ","Failed"]})]})}function te(e){var n=e.data,t=e.name,h=n.datasource,v=n.tables[t];return(0,d.h5)(d.vT.safeParse(v)),(0,d.h5)(U.U0.safeParse(h)),(0,o.j)(t),(0,u.L)({eventName:c.m.PAGE_VIEW,eventProperties:{type:"single-report",tab:"Profiling"}}),n?(0,x.jsx)(s.o,{children:(0,x.jsxs)(r.kC,{direction:"column",minH:"calc(100vh + 1px)",width:"100%",children:[(0,x.jsx)(r.kC,{mx:"5%",mt:4,children:(0,x.jsxs)(i.aG,{fontSize:"lg",children:[(0,x.jsx)(i.gN,{children:(0,x.jsx)(l.rU,{href:"/",children:(0,x.jsx)(i.At,{href:"/","data-cy":"sr-report-breadcrumb-back",children:h.name})})}),(0,x.jsx)(i.gN,{isCurrentPage:!0,children:(0,x.jsx)(i.At,{href:"#",children:v.name})})]})}),(0,x.jsxs)(r.kC,{border:"1px solid",borderColor:"gray.300",bg:"white",borderRadius:"md",p:6,mt:3,mx:"5%",direction:"column",children:[(0,x.jsx)(ne,{table:v}),(0,x.jsxs)(a.mQ,{isLazy:!0,children:[(0,x.jsxs)(a.td,{children:[(0,x.jsx)(a.OK,{onClick:function(){(0,c._)({eventName:c.m.PAGE_VIEW,eventProperties:{type:"single-report",tab:"Profiling"}})},children:"Profiling"}),(0,x.jsx)(a.OK,{"data-cy":"sr-report-tab-item",onClick:function(){(0,c._)({eventName:c.m.PAGE_VIEW,eventProperties:{type:"single-report",tab:"Tests"}})},children:"Tests"}),v.dbt_assertion_result&&(0,x.jsx)(a.OK,{onClick:function(){(0,c._)({eventName:c.m.PAGE_VIEW,eventProperties:{type:"single-report",tab:"dbt Tests"}})},children:"dbt Tests"})]}),(0,x.jsxs)(a.nP,{children:[(0,x.jsx)(a.x4,{children:(0,x.jsx)(M,{data:v.columns})}),(0,x.jsx)(a.x4,{children:(0,x.jsx)($,{assertionData:v.piperider_assertion_result})}),(null===v||void 0===v?void 0:v.dbt_assertion_result)&&(0,x.jsx)(a.x4,{children:(0,x.jsx)($,{type:"dbt",assertionData:v.dbt_assertion_result})})]})]})]})]})}):(0,x.jsx)(s.o,{children:(0,x.jsx)(r.kC,{justifyContent:"center",alignItems:"center",minHeight:"100vh",children:"No profile data found."})})}},6786:function(e,n,t){t.d(n,{L:function(){return l}});var r=t(1413),i=t(2791),a=t(3442);function l(e){(0,i.useEffect)((function(){(0,a._)((0,r.Z)({},e))}),[])}},8453:function(e,n,t){t.d(n,{y:function(){return a}});var r=t(885),i=t(2791);function a(e){var n=(0,i.useState)(null),t=(0,r.Z)(n,2),a=t[0],l=t[1];return(0,i.useEffect)((function(){if(e&&e.current){var n=e.current,t=new ResizeObserver((function(e){e.forEach((function(e){l(e.contentRect)}))}));return t.observe(n),function(){t.unobserve(n)}}}),[e]),a}},3442:function(e,n,t){t.d(n,{_:function(){return a},m:function(){return i}});var r=t(8083),i={PAGE_VIEW:"Page View"};function a(e){var n=e.eventName,t=e.eventProperties,i=e.eventOptions;return window.PIPERIDER_METADATA.amplitude_api_key?(0,r.j)(n,t,i):console.info({eventName:n,eventProperties:t,eventOptions:i})}},9842:function(e,n,t){t.d(n,{p:function(){return v},v:function(){return h}});var r=t(9227),i=t(2387),a="var(--chakra-space-2)",l="var(--chakra-space-2)",s="var(--chakra-space-4)",o="var(--chakra-space-4)",u="var(--chakra-radii-md)",c="var(--chakra-colors-white)",d="var(--chakra-colors-blackAlpha-700)";function h(e){var n=e.target,t=e.style,i=void 0===t?{}:t;return r.Ys(n).append("div").attr("class","chart_tooltip").style("visibility","hidden").style("position","absolute").style("z-index","1501").style("padding-top",(null===i||void 0===i?void 0:i.paddingTop)||a).style("padding-bottom",(null===i||void 0===i?void 0:i.paddingBottom)||l).style("border-radius",(null===i||void 0===i?void 0:i.borderRadius)||u).style("padding-left",(null===i||void 0===i?void 0:i.paddingLeft)||s).style("padding-right",(null===i||void 0===i?void 0:i.paddingRight)||o).style("color",(null===i||void 0===i?void 0:i.color)||c).style("background-color",(null===i||void 0===i?void 0:i.backgroundColor)||d)}function v(e){var n=e.type;return e.isCategorical?i.bF:"string"===n?i.d4:"boolean"===n?i.RW:"datetime"===n?i.qI:i.E5}},922:function(e,n,t){t.d(n,{G_:function(){return l},JH:function(){return o},WN:function(){return a},cc:function(){return u},gQ:function(){return s}});var r=t(2982),i=t(885);function a(e,n){var t={};return Object.entries(e||{}).forEach((function(e){var n=(0,i.Z)(e,2),r=n[0],a=n[1];t[r]||(t[r]={}),t[r].base=a})),Object.entries(n||{}).forEach((function(e){var n=(0,i.Z)(e,2),r=n[0],a=n[1];t[r]||(t[r]={}),t[r].target=a})),t}function l(e){var n=e.base,t=e.target,i=new Map;if(!n||!t)return null;var a=n.labels.map((function(e,t){return i.set(e||String(t),t),{label:e,base:n.counts[t],target:0}}));return t.labels.reduce((function(e,n,a){var l=n||String(a),s=i.has(l),o=t.counts[a];if(s)return e[i.get(l)].target=o,e;var u={label:n,base:0,target:o};return[].concat((0,r.Z)(e),[u])}),a)}function s(e){var n=e.nulls,t=e.non_nulls,r=e.total,i=e.invalids,a=e.distinct,l=e.valids,s=e.non_duplicates,o=e.duplicates,u=e.zero_length,c=e.negatives,d=e.zeros;return{negativesOfTotal:c&&r?c/r:null,zerosOfTotal:d&&r?d/r:null,hasNoNull:t===r,zeroLengthOfTotal:u&&r?u/r:null,distinctOfTotal:a&&r?a/r:null,validsOfTotal:l&&r?l/r:null,invalidsOfTotal:i&&r?i/r:null,nullsOfTotal:n&&r?n/r:null,duplicatesOfTotal:o&&r?o/r:null,nonDuplicatesOfTotal:s&&r?s/r:null,totalOfTotal:r?r/r:null}}function o(e){var n=e.distinct,t=e.type;return"number"===typeof n&&(n<=100&&("string"===t||"integer"===t))}function u(e){if(e){var n=e.topk,t=e.histogram,r=e.trues,i=e.falses,a=e.type,l=e.total,s=o(e),u="boolean"===a,c=s?null===n||void 0===n?void 0:n.values:u?["TRUES","FALSES"]:null===t||void 0===t?void 0:t.labels,d=s?null===n||void 0===n?void 0:n.counts:u?[r,i]:null===t||void 0===t?void 0:t.counts;return c&&d&&l?c.map((function(e,n){return{label:e,isCategorical:s,value:d[n],type:a,total:l}})):void 0}}}}]);
//# sourceMappingURL=543.af129358.chunk.js.map