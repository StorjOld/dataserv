import RandomIO

path = RandomIO.RandomIO('seed string').genfile(50)
with open(path,'rb') as f:
    print(f.read())