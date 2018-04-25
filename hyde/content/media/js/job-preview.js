(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["base.j2"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
(parentTemplate ? function(e, c, f, r, cb) { cb(""); } : context.getBlock("main"))(env, context, frame, runtime, function(t_2,t_1) {
if(t_2) { cb(t_2); return; }
output += t_1;
output += "\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
});
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
function b_main(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var frame = frame.push(true);
output += "\n";
cb(null, output);
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
b_main: b_main,
root: root
};

})();
})();
(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["job.j2"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
env.getTemplate("base.j2", true, "job.j2", false, function(t_3,t_2) {
if(t_3) { cb(t_3); return; }
parentTemplate = t_2
for(var t_1 in parentTemplate.blocks) {
context.addBlock(t_1, parentTemplate.blocks[t_1]);
}
output += "\n\n";
(parentTemplate ? function(e, c, f, r, cb) { cb(""); } : context.getBlock("endhead"))(env, context, frame, runtime, function(t_5,t_4) {
if(t_5) { cb(t_5); return; }
output += t_4;
output += "\n\n";
(parentTemplate ? function(e, c, f, r, cb) { cb(""); } : context.getBlock("main"))(env, context, frame, runtime, function(t_7,t_6) {
if(t_7) { cb(t_7); return; }
output += t_6;
output += "\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
})})});
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
function b_endhead(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var frame = frame.push(true);
output += "\n    <meta property=\"og:site_name\" content=\"The Free Python Job Board\"/>\n    <meta property=\"og:title\" content=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"company"), env.opts.autoescape);
output += ": ";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"title"), env.opts.autoescape);
output += "\"/>\n    <meta property=\"og:type\" content=\"website\"/>\n    <meta property=\"og:image\" content=\"http://pythonjobs.github.io/touch-icon-ipad-retina.png\" />\n    <meta property=\"og:description\" content=\"";
output += runtime.suppressValue(env.getFilter("truncate").call(context, env.getFilter("striptags").call(context, env.getFilter("typogrify").call(context, env.getFilter("markdown").call(context, runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"detail")))),220), env.opts.autoescape);
output += "\" />\n    <meta property=\"og:url\" content=\"";
output += runtime.suppressValue((lineno = 8, colno = 46, runtime.callWrap(runtime.contextOrFrameLookup(context, frame, "full_url"), "full_url", context, [runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"url")])), env.opts.autoescape);
output += "\" />";
cb(null, output);
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
function b_main(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var frame = frame.push(true);
output += "<nav class=\"main\">\n    <a class=\"backlink\" href=\"";
output += runtime.suppressValue((lineno = 13, colno = 42, runtime.callWrap(runtime.contextOrFrameLookup(context, frame, "content_url"), "content_url", context, [runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"node")),"parent")),"url")])), env.opts.autoescape);
output += "\">\n        <i class='i-list'></i>\n        Back to list\n    </a>\n    ";
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"prev_by_time")) {
output += "\n    <a class=\"prev\"\n        title=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"prev_by_time")),"meta")),"title"), env.opts.autoescape);
output += "\"\n        href=\"";
output += runtime.suppressValue((lineno = 20, colno = 26, runtime.callWrap(runtime.contextOrFrameLookup(context, frame, "content_url"), "content_url", context, [runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"prev_by_time")),"url")])), env.opts.autoescape);
output += "\">\n        <i class='i-left'></i>\n        Previous Job\n    </a>\n    ";
;
}
output += "\n\n    ";
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"next_by_time")) {
output += "\n    <a class=\"next\"\n        title=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"next_by_time")),"meta")),"title"), env.opts.autoescape);
output += "\"\n        href=\"";
output += runtime.suppressValue((lineno = 29, colno = 26, runtime.callWrap(runtime.contextOrFrameLookup(context, frame, "content_url"), "content_url", context, [runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"next_by_time")),"url")])), env.opts.autoescape);
output += "\">\n        Next Job <i class='i-right'></i>\n    </a>\n    ";
;
}
output += "\n\n    <a class=\"problem\"\n    href=\"https://github.com/pythonjobs/jobs/issues\">\n    Report a problem\n    </a>\n</nav>\n\n<article class=\"job\">\n    <h1>\n            ";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"title"), env.opts.autoescape);
output += "\n    </h1>\n    <div class=\"head\">\n        Posted by\n        <span>\n            ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url")) {
output += "\n            <a href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url"), env.opts.autoescape);
output += "\" target=\"_blank\">\n            ";
;
}
output += "\n                <i class=\"i-company\"></i>\n                ";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"company"), env.opts.autoescape);
output += "\n            ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url")) {
output += "\n            </a>\n            ";
;
}
output += "\n        </span>\n        on\n        <span>\n            <i class=\"i-calendar\"></i>\n            ";
output += runtime.suppressValue((lineno = 59, colno = 43, runtime.callWrap(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"created")),"strftime"), "resource[\"meta\"][\"created\"][\"strftime\"]", context, ["%a, %d %b %Y"])), env.opts.autoescape);
output += "\n        </span>\n        <div>\n        Contract type: <span>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"contract"), env.opts.autoescape);
output += "</span>.  Location: <span>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"location"), env.opts.autoescape);
output += "</span>\n        </div>\n        ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"tags")) {
output += "\n        <div class=\"tags\">\n            <i class=\"i-tag\"></i> Tags:\n            <ul class=\"tags clear\">\n                ";
frame = frame.push();
var t_10 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"tags");
if(t_10) {t_10 = runtime.fromIterator(t_10);
var t_9 = t_10.length;
for(var t_8=0; t_8 < t_10.length; t_8++) {
var t_11 = t_10[t_8];
frame.set("tag", t_11);
frame.set("loop.index", t_8 + 1);
frame.set("loop.index0", t_8);
frame.set("loop.revindex", t_9 - t_8);
frame.set("loop.revindex0", t_9 - t_8 - 1);
frame.set("loop.first", t_8 === 0);
frame.set("loop.last", t_8 === t_9 - 1);
frame.set("loop.length", t_9);
output += "\n                    <li>\n                        <a class=\"tag\" href=\"";
output += runtime.suppressValue((lineno = 70, colno = 57, runtime.callWrap(runtime.contextOrFrameLookup(context, frame, "content_url"), "content_url", context, ["tags/" + "" + env.getFilter("lower").call(context, t_11) + "" + ".html"])), env.opts.autoescape);
output += "\">\n                            ";
output += runtime.suppressValue(env.getFilter("lower").call(context, t_11), env.opts.autoescape);
output += "\n                        </a>\n                    </li>\n                ";
;
}
}
frame = frame.pop();
output += "\n            </ul>\n        </div>\n        ";
;
}
output += "\n    </div>\n\n    <div class=\"contact\">\n        <h1>Contact</h1>\n        <div class=\"field\">\n            Name: <span>";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"contact")),"name"), env.opts.autoescape);
output += "</span>\n        </div>\n        <div class=\"field\">\n            Email: <span><a href=\"mailto:";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"contact")),"email"), env.opts.autoescape);
output += "?subject=pythonjobs.github.io - ";
output += runtime.suppressValue(env.getFilter("urlencode").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"title")), env.opts.autoescape);
output += "\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"contact")),"email"), env.opts.autoescape);
output += "</a></span>\n        </div>\n        ";
if(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url")) {
output += "\n        <div class=\"field\">\n            Website: <span><a href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url"), env.opts.autoescape);
output += "\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"url"), env.opts.autoescape);
output += "</a></span>\n        </div>\n        ";
;
}
output += "\n        ";
frame = frame.push();
var t_14 = runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "resource")),"meta")),"contact");
if(t_14) {t_14 = runtime.fromIterator(t_14);
var t_12;
if(runtime.isArray(t_14)) {
var t_13 = t_14.length;
for(t_12=0; t_12 < t_14.length; t_12++) {
var t_15 = t_14[t_12][0];
frame.set("[object Object]", t_14[t_12][0]);
var t_16 = t_14[t_12][1];
frame.set("[object Object]", t_14[t_12][1]);
frame.set("loop.index", t_12 + 1);
frame.set("loop.index0", t_12);
frame.set("loop.revindex", t_13 - t_12);
frame.set("loop.revindex0", t_13 - t_12 - 1);
frame.set("loop.first", t_12 === 0);
frame.set("loop.last", t_12 === t_13 - 1);
frame.set("loop.length", t_13);
output += "\n            ";
if(runtime.inOperator(t_15,["name","url","email"])) {
output += "\n            ";
;
}
else {
output += "\n                <div class=\"field\">\n                    ";
output += runtime.suppressValue(env.getFilter("title").call(context, t_15), env.opts.autoescape);
output += ": <span>";
output += runtime.suppressValue(t_16, env.opts.autoescape);
output += "</span>\n                </div>\n            ";
;
}
output += "\n        ";
;
}
} else {
t_12 = -1;
var t_13 = runtime.keys(t_14).length;
for(var t_17 in t_14) {
t_12++;
var t_18 = t_14[t_17];
frame.set("key", t_17);
frame.set("value", t_18);
frame.set("loop.index", t_12 + 1);
frame.set("loop.index0", t_12);
frame.set("loop.revindex", t_13 - t_12);
frame.set("loop.revindex0", t_13 - t_12 - 1);
frame.set("loop.first", t_12 === 0);
frame.set("loop.last", t_12 === t_13 - 1);
frame.set("loop.length", t_13);
output += "\n            ";
if(runtime.inOperator(t_17,["name","url","email"])) {
output += "\n            ";
;
}
else {
output += "\n                <div class=\"field\">\n                    ";
output += runtime.suppressValue(env.getFilter("title").call(context, t_17), env.opts.autoescape);
output += ": <span>";
output += runtime.suppressValue(t_18, env.opts.autoescape);
output += "</span>\n                </div>\n            ";
;
}
output += "\n        ";
;
}
}
}
frame = frame.pop();
output += "\n    </div>\n\n\n    <div class=\"body\">\n        ";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.contextOrFrameLookup(context, frame, "detail")), env.opts.autoescape);
output += "\n    </div>\n\n</article>";
cb(null, output);
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
b_endhead: b_endhead,
b_main: b_main,
root: root
};

})();
})();

