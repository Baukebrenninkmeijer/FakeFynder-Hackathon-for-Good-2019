# Deepfake detection for the masses
In our submission for the Hackathon for Good, we created a working POC which is a website where people can easily paste youtube links or upload videos to have them be checked for manipulated sections. The deepfake detection is done using the model from FaceForensics++, which has around 80% accuracy on a combination of compressed videos, but achieves around 99% accuracy on a single type of compression. 

The POC also allows for easy checking whether a video has been seen before with a database of video hashes which can be searched. 

![website usage](images/website_usage.gif)

For usage, one needs to download the model weights from the [FaceForensics repository](https://github.com/ondyari/FaceForensics) and put them in `classification/weights`. 
