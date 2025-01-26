To run it, you need the models which are used in colorizing the images.
Create a folder named "models" and add three models into the folder
1. Download colorization_deploy_v2.prototxt from https://github.com/richzhang/colorization/tree/caffe/colorization/models
2. https://github.com/richzhang/colorization/blob/caffe/colorization/resources/pts_in_hull.npy
3. https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbkxaQWpnWm1oenZudWVFelNodl8xZlc1VjZQQXxBQ3Jtc0trdngwT212MUR1SVl0X0VrZkMwN2lMQWNYUnJsWUpIYnV0VmQ1NE5xTnU5cHJTY2dWUHBtNFFGOUJ4NlhvQXRfaWprb2lLMTJzenM0NGZxSHN6Smp1ZFdPNmt3VnZBaExjV0RRTlZCMnlaanh1Z2tXcw&q=https%3A%2F%2Fwww.dropbox.com%2Fs%2Fdx0qvhhp5hbcx7z%2Fcolorization_release_v2.caffemodel%3Fdl%3D1&v=gAmskBNz_Vc

The images uploaded by the user are stored inside a folder and deleted later, so you also need to create a "static/uploads" folder

Use "pip install -r requirements.txt" to install all the requirements for this project
