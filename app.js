const form=document.getElementById("chatForm");
const input=document.getElementById("promptInput");
const messages=document.getElementById("messages");
const welcome=document.getElementById("welcome");
const sendButton=document.getElementById("sendButton");
const modelSelect=document.getElementById("modelSelect");
const statusDot=document.getElementById("statusDot");
const statusText=document.getElementById("statusText");
let history=[];
function addMessage(role,text,extra=""){
  welcome.hidden=true;
  const row=document.createElement("div");row.className="message "+role+" "+extra;
  const bubble=document.createElement("div");bubble.className="bubble";
  if(role!=="user"){const who=document.createElement("div");who.className="who";who.textContent=role==="error"?"Connection issue":"BudgieOS AI";bubble.appendChild(who)}
  const p=document.createElement("p");p.textContent=text;bubble.appendChild(p);row.appendChild(bubble);messages.appendChild(row);row.scrollIntoView({behavior:"smooth",block:"end"});return row;
}
async function checkStatus(){
  try{const r=await fetch("/api/health");const d=await r.json();statusDot.className="status-dot "+(d.available?"online":"offline");statusText.textContent=d.available?"AI provider connected":"No AI provider connected";}
  catch{statusDot.className="status-dot offline";statusText.textContent="Start the local server to connect";}
}
async function sendMessage(text){
  const prompt=text.trim();if(!prompt)return;
  addMessage("user",prompt);history.push({role:"user",content:prompt});input.value="";input.style.height="auto";sendButton.disabled=true;
  const waiting=addMessage("assistant","Thinking…");waiting.querySelector("p").className="typing";
  try{
    const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({messages:history,model:modelSelect.value})});
    const data=await response.json();if(!response.ok)throw new Error(data.error||"The AI request failed.");
    waiting.remove();const answer=data.reply||"The provider returned an empty response.";history.push({role:"assistant",content:answer});addMessage("assistant",answer);
  }catch(error){waiting.remove();history.pop();addMessage("error",error.message,"error");}
  finally{sendButton.disabled=false;input.focus();checkStatus();}
}
form.addEventListener("submit",e=>{e.preventDefault();sendMessage(input.value)});
input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();form.requestSubmit()}});
input.addEventListener("input",()=>{input.style.height="auto";input.style.height=Math.min(input.scrollHeight,180)+"px"});
document.querySelectorAll(".suggestion").forEach(button=>button.addEventListener("click",()=>sendMessage(button.dataset.prompt)));
document.getElementById("newChat").addEventListener("click",()=>{history=[];messages.replaceChildren();welcome.hidden=false;input.focus();document.getElementById("sidebar").classList.remove("open")});
document.getElementById("clearChat").addEventListener("click",()=>{history=[];messages.replaceChildren();welcome.hidden=false});
document.getElementById("mobileMenu").addEventListener("click",()=>document.getElementById("sidebar").classList.toggle("open"));
checkStatus();