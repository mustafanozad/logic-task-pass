sentence = str(input ("Please, Enter the stgring: ")) 
character = str(input ("Please, Enter the character: ")) 
count = 0
for i in sentence:
    if i == character:
        count = count + 1
print(count)
