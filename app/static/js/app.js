

document.getElementById("inp-text").focus();
document.getElementsByTagName("body")[0].addEventListener("keypress",function(e){
   if(e.key =='Enter')
    send();
});
document.getElementById("send").addEventListener("click",send);

function send() {
    let text = document.getElementById("inp-text").value.trim();
    if(text ==''){
        alert("من فضلك ادخل جملة لكي نرد عليك !");
        return;
    } else {
        let request = document.createElement("div");
        request.className = "request";
        request.innerText = text;
        document.getElementsByClassName("main-chatbot")[0].appendChild(request);
        document.getElementById("inp-text").value='';
        document.getElementById("spinner").classList.toggle("d-none");
        let headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }
        let body = {
            "model" : "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": text}],
            "temperature": 0.7,
        }
        
       fetch('https://api.openai.com/v1/chat/completions',{
        method:"post",
        mode: "cors",
        headers: headers,
        body: JSON.stringify(body)})
        .then(response => response.json())
        .then(function(data) {
            let resText  = data.choices[0].message.content;
            let response = document.createElement("div");
            response.className = "response";
            response.innerText = resText;
            setTimeout(function(){
                
                document.getElementsByClassName("main-chatbot")[0].appendChild(response);
                document.getElementById("spinner").classList.toggle("d-none");
                var scroll = document.getElementsByClassName('main-chatbot')[0].scrollHeight;
                document.getElementsByClassName('main-chatbot')[0].scrollTop = scroll+100;
                 
            }, 1000)
        })
    }
    var scroll = document.getElementsByClassName('main-chatbot')[0].scrollHeight;
    document.getElementsByClassName('main-chatbot')[0].scrollTop = scroll
}
