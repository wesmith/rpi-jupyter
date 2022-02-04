%# led_web_control.tpl: WESmith updated 01/04/22

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
    <link href="/static/{{css_file}}"
     rel="stylesheet" type="text/css">
  </head>
  
  <body>
    <h1>{{name1}}</h1>
    <h2>{{name2}}</h2>
        
    <br></br>
    <table class="center">

    %for row in table1:
        <tr>
        %for col in row:
            <td><h2>{{col}}</h2></td>
        %end
        </tr>
    %end

    </table>

    <script>
    function changed(led)
    {window.location.href='/' + led}  
    </script>
    
    <br></br>
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