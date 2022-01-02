%# led_web_template.tpl: WESmith 12/29/121

<!DOCTYPE html>
<html>

<style>
.button {
  background-color: transparent;
  color: rgb(250, 250, 250);
  font-size: 4rem;
  margin: 10px 15px;
  border: none;  %# doesn_t seem to work
}
</style>

  <head>
    <meta charset="utf-8">
    <title>{{name1}}</title>
    <link href="/static/minimal-table.css" 
     rel="stylesheet" type="text/css">
  </head>
  
  <body>
    <h1>{{name1}}</h1>
    <h2>{{name2}}</h2>
        
    <script>
    function changed(led)
    {window.location.href='/' + led}  
    </script>
    
    <table class="center">
    
    %for j, k in enumerate(buttons):
        <tr>
        <td>
        <input type='button' class='button'
          onClick='changed({{j}})' 
          value={{k}}>
        </td>
        </tr>
    %end
    
    </table>

  </body>
  
</html>