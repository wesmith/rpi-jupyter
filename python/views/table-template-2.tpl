%# table-template-2.tpl: WESmith 12/24/21, table testing in bottle.py

<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{name1}}</title>
    <link href="/static/minimal-table.css" rel="stylesheet" type="text/css">
  </head>
  <body>
    <h1>{{name1}}</h1>
    
        <table class="center">
        
        %for row in table1:
            <tr>
            %for col in row:
                <td><h2>{{col}}</h2></td>
            %end
            </tr>
        %end
        
        </table>
    
    <h3>{{name2}}</h3>

        <table class="center">

        %for row in table2:
            <tr>
            %for col in row:
                <td><h4><center>{{col}}</center></h4></td>
            %end
            </tr>
        %end

        </table>

  </body>
</html>