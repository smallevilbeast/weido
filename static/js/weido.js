Overload = function(fn_objs){
    var is_match = function(x,y){
        if(x==y)return true;
        if(x.indexOf("*")==-1)return false;
     
        var x_arr = x.split(","),y_arr = y.split(",");
        if(x_arr.length != y_arr.length)return false;
     
        while(x_arr.length){
            var x_first =  x_arr.shift(),y_first = y_arr.shift();
            if(x_first!="*" && x_first!=y_first)return false;
        }
        return true;
    };
    var ret = function(){
        var args = arguments
        ,args_len = args.length
        ,args_types=[]
        ,args_type
        ,fn_objs = args.callee._fn_objs
        ,match_fn = function(){};
         
        for(var i=0;i<args_len;i++){
            var type = typeof args[i];
            type=="object" && (args[i].length>-1) && (type="array");
            args_types.push(type);
        }
        args_type = args_types.join(",");
        for(var k in fn_objs){
            if(is_match(k,args_type)){
                match_fn = fn_objs[k];
                break;
            }
        }
        return match_fn.apply(this,args);
    };
    ret._fn_objs = fn_objs;
    return ret;
};
 
String.prototype.format = Overload({
    "array" : function(params){
        var reg = /{(\d+)}/gm;
        return this.replace(reg,function(match,name){
            return params[~~name];
        });
    }
    ,"object" : function(param){
        var reg = /{([^{}]+)}/gm;
        return this.replace(reg,function(match,name){
            return param[name];
        });
    }
});


function hello(data){
	var base_div = '<div class="message"><div class="split_line"></div><img class="profile_image" width=20 height=20 src={profile_image} alt="" /><div class="content"><span class="username">{name}</span><span class="text">{text}</span>{thumbnail}{retweeted}<div class="info"><span class="created_at">{created_at} </span><span class="source">{source}</span></div><div class="action"><span class="line_split"> | </span><div class="repost"></div><span class="reposts_count">{reposts_count}</span><div class="comment"></div><span class="comments_count">{comments_count}</span></div></div></div>'
	var thumbnail_div = '<img class="thumbnail" src={thumbnail_pic} />'
	var retweeted_div = '<div class="retweeted"><span class="ret_name">@{name}: </span><span class="ret_text">{text}</span><div class="prompt"><span class="reposts_prompt">转发</span><span class="reposts_count">({reposts_count})</span><span class="comments_prompt">评论</span><span class="comments_count">({comments_count})</span></div>{thumbnail}</div>'
	var delete_retweeted_div = '<div class="retweeted"><span class="ret_text">{text}</span></div>'
	
	for (var i=0; i<data.length; i++){
		
		var message = data[i];
		var base_thumbnail_div = null;
		var retweeted = null;
		var retweeted_thumbnail_div = null;		
		
		function replace_call(text){

			// console.log(text);
			
			var topics_text = text.replace(/(#.*?#)/g, '<span class="topics">$1</span>');
			var url_text = topics_text.replace(/(http:\/\/t\.cn\/[a-zA-Z0-9-]+)/g, '<a href=$1 class="lower_url">$1</a>');
			var call_text = url_text.replace(/(@\S+?)[\)|\s|:]|(@\S+)/g, '<span class="call_user">$1 </span>');			
			return call_text;

		}
		
		if (message.hasOwnProperty("thumbnail_pic")){
			base_thumbnail_div = thumbnail_div.format({"thumbnail_pic" : message.thumbnail_pic});
		}
		
		if (message.hasOwnProperty("retweeted_status")){
			if (message.retweeted_status.hasOwnProperty("thumbnail_pic")){
				retweeted_thumbnail_div = thumbnail_div.format({"thumbnail_pic" : message.retweeted_status.thumbnail_pic});
			}
			if (message.retweeted_status.user instanceof Object){
				var name = message.retweeted_status.user.name; // this message is delete!
				retweeted = retweeted_div.format({"name" : name,
												  "text" : replace_call(message.retweeted_status.text),
												  "reposts_count": message.retweeted_status.reposts_count,
												  "comments_count": message.retweeted_status.comments_count,
												  "thumbnail" : retweeted_thumbnail_div});
				
			} else {
				retweeted = delete_retweeted_div.format({"text" : replace_call(message.retweeted_status.text)});
			}
		}
		
		message_div = base_div.format({
			"profile_image": message.user.profile_image_url,
			"name" : message.user.name, 
			"text": replace_call(message.text),
			"created_at": message.created_at,
			"source" : message.source,
			"thumbnail" : base_thumbnail_div,
			"retweeted" : retweeted,
			"reposts_count" : !message.reposts_count?"":message.reposts_count,
			"comments_count" : !message.comments_count?"":message.comments_count,
		}).replace(/null/g, "").replace(/undefined/g, "");
		
		$(".timeline").append(message_div);
		}
}

