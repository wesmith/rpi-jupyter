%# table-template-2.tpl: WESmith 12/24/21, table testing in bottle.py

<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Table Template</title>
    %#<link href="/home/pi/Devel/raspberry_pi/rpi-jupyter/python/static/css/minimal-table.css" rel="stylesheet" type="text/css">
  </head>
  <body>
    <h1>{{name1}}</h1>
    
        %for row in list:
            <p><h2>{{row}}</h2></p>
        %end
    
    <h2>{{name2}}</h2>

        <table border="5">

        %for row in table:
            <tr>
            %for col in row:
                <td><h3><center>{{col}}<c/enter></h3></td>
            %end
            </tr>
        %end

        </table>

  </body>
</html>