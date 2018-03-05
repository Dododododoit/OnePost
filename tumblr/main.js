// Authenticate via OAuth
var tumblr = require('tumblr.js');
var url = "";
var client = tumblr.createClient({
  consumer_key: 'p9mbX6gxaTqkFoZfhyztVg3sBRPbvCvdRdl1Kr7q04LcnBW9bn',
  consumer_secret: 'qrtRnVNHnl0LBsZATg2piY7lsUQ1oHyxkeWykjwyApWWFtsOxA',
  token: '9lw7mWVaZrfq565K0MAGDefPiDm3kIRBL9oZE4bvnvZJ6xKTOk',
  token_secret: 'tq9HPQEkZzIhzcgB4w0QFxUl2yLl9djzFDJERq8xwpPlqn3QqC'
});

// Make the request
client.userInfo(function(err, data) {
  data.user.blogs.forEach(function(blog) {
  	var name = blog.name;
    console.log(blog.name);
   	//alert(name);
    var method = 'POST';
    var url = 'http://api.tumblr.com/v2/blog/' + name + '.tumblr.com/post';

  });
});

client.blogInfo('weexdee.tumblr.com', function (err, data) {
  if (err) {
    console.log(err);
  } else {
    console.log(JSON.stringify(data));
  }
});

client.createTextPost('weexdee.tumblr.com', {body:`image is dead`}, function (err, data) {
  if (err) {
    console.log(err);
  } else {
    console.log(JSON.stringify(data));
  }
});