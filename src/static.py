head = """
<html>
<head>
<style>
    body {
        background-color: white;
    }
    .header {
        display: in-line;
    }
    
    td {
        border: 1px solid black;
        text-align: center;
    }
</style>
</head>
<body>
<center>
<h2>API Status</h2>
<table>
"""

footer = """
</table>
</center>
<script>
const queueDownload = async (download, ele) => {
        const response = await fetch('download?video=' + download,
            {headers: {
            'Access-Control-Allow-Origin':'*',
            }});
        const myJson = await response.json(); //extract JSON from the http response
        ele.setAttribute("disabled", true);
        await console.log(myJson)
    }
</script>
</body>
</html>
"""


hash_page = """
    <html>
    <head>
    <style>
    h6 {
        color: red;
    }
    </style>
    </head>
    <body>
    <center>
    <h3>Enter your password here, this will generate a hash that you can send to the linux admins for your account creation</h3>
    <h6>**No passwords or files generated are stored or logged. Hashes are salted for security reasons.**</h6>
    <input type="password" name="hash" id="hash" width=40><br><br><br>
    <button type="button" onclick="getHash()">Submit</button>
    <br><br>
    <p>Hash to send: <p id="derp"></p></p>
    </center>
    <script>
        function download_keys() {
            location.href='/generate_keys'
        }
        const getHash = async () => {
            var hash = document.getElementById('hash').value
            const response = await fetch('/generate_hash_post',
                {
                    method: "POST",
                    body: JSON.stringify({'hash':hash}),
                    headers: {
                    'Access-Control-Allow-Origin':'*',
                    }
                }
            );
            const myJson = await response.json(); //extract JSON from the http response
            await console.log(myJson.hash);
            var link = 
            document.getElementById('derp').innerHTML = myJson.hash + '<br><br><h4>Use the button below to download your keypairs. You will need to send the public key to the admin.<br>Keep your private key safe, you will need to use this for future authentication.<h4><br><button onclick="download_keys()">Get Keys</button>';
        }
    </script>
    </body>
    </html>
"""