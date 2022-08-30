Python 3.10.6 (tags/v3.10.6:9c7b4bd, Aug  1 2022, 21:53:49) [MSC v.1932 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
str = "Engineering"
   
 
print ("Original string: " + str) 
   
 
res_str = str.replace('e', '') 
   

print ("The string after removal of character: " + res_str) 
 
res_str = str.replace('e', '', 1) 
    
print ("The string after removal of character: " + res_str) 