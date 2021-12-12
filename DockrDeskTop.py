from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import docker
import threading

# Connect to docker
try:
    client = docker.from_env()
except:
    messagebox.showinfo("error", "Check docker.\nNote: you might need to register as sudo ")
    exit()

# Returns all containers in server
def getContainerList(*args):
  try:
    containersListBox.delete(0, END)
    containers = client.containers.list(all=True)
    # Looping on containers
    for i in range(len(containers)):
      containersListBox.insert(i, containers[i].name)
      # Check for status and color the item
      if (containers[i].status == 'running'):
        containersListBox.itemconfig(i, {'fg':'green'})
      else:
        containersListBox.itemconfig(i, {'fg':'red'})
  except Exception as e: # Catch all exceptions (Thrown errors)
    messagebox.showinfo("Error", e)

# Returns all images in server
def getImageList(*args):
  try:
    imagesListBox.delete(0, END)
    images = client.images.list(all=True)
    # Looping on images
    for i in range(len(images)):
      image = images[i]
   # Assuming an image always has at least one tag
      for j in range(len(image.tags)):
        imagesListBox.insert(END, image.tags[j]) # Insert the image (with tag name) to the end of the list
  except Exception as e:
    messagebox.showinfo("Error", e)

# Runs the actual image pulling on another thread
def downloadImageThread(*args):
  try:
    threading.Thread(target=downloadImage).start()
  except:
    messagebox.showinfo("Error", "Issue while starting new thread")

# Pulls the image name provided from docker
def downloadImage(*args):
  try:
    imageNameText = imageName.get()
    client.images.pull(imageNameText)
    getImageList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# Create a new container from selected image
def createContainer():
  try:
    # Launch dialog to ask for container name
    containerName = simpledialog.askstring(title='New container', prompt='Please enter the new container name')
    # Check dialog wasn't cancelled
    if (containerName == None):
      return
    selectedImage = imagesListBox.get(ACTIVE)
    client.containers.create(image=selectedImage, name=containerName)
    getContainerList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# Remove an image
def removeImage():
  try:
    selectedImage = imagesListBox.get(ACTIVE) # Get currently selected image
    # Display Ok/Cancel message to ask if sure
    if(messagebox.askokcancel('Warning', 'Are you sure you want to delete {} image?'.format(selectedImage))):
      client.images.remove(selectedImage)
      getImageList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# Starts a container
def startContainer():
  try:
    selectedContainer = containersListBox.get(ACTIVE)
    container = client.containers.get(selectedContainer)
    container.start()
    getContainerList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# stops a running container
def stopContainer():
  try:
    selectedContainer = containersListBox.get(ACTIVE)
    container = client.containers.get(selectedContainer)
    container.stop()
    getContainerList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# Remove a container
def removeContainer():
  try:
    selectedContainer = containersListBox.get(ACTIVE)
    # Display Ok/Cancel message to ask if sure
    if(messagebox.askokcancel('Warning', 'Are you sure you want to delete {} container?'.format(selectedContainer))):
      container = client.containers.get(selectedContainer)
      container.remove()
      getContainerList()
  except Exception as e:
    messagebox.showinfo("Error", e)

# Start root instance
root = Tk()
root.title("Docker Manager")


# Configure frame
mainframe = ttk.Frame(root, padding='20 20 20 20')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

# Input label
ttk.Label(mainframe, text='Image Name', font=("Arial",10, "bold")).grid(column=1, row=1, sticky=W)

# Image name input
imageName = StringVar() # StringVar is a tkinter special data type
imageNameEntry = ttk.Entry(mainframe, width=30, textvariable=imageName)
imageNameEntry.grid(column=1, row=1, sticky=(S, E))

# Get image button
ttk.Button(mainframe, text='Pull', command=downloadImageThread).grid(column=2, row=1, sticky=(S, W))

# Images list
ttk.Label(mainframe, text='Images List', font=("Arial",14, "bold")).grid(column=1, row=2, sticky=W)
imagesListBox = Listbox(mainframe, width=50)
imagesListBox.grid(column=1, row=3)

# Image list button group
imgListButtonFrame = Frame(mainframe)
imgListButtonFrame.grid(column=1, row=4, sticky=(N, W, E, S))
ttk.Button(imgListButtonFrame, text='create', command=createContainer).grid(column=1, row=1, sticky=W)
ttk.Button(imgListButtonFrame, text='delete', command=removeImage).grid(column=2, row=1, sticky=W)

# Containers list
ttk.Label(mainframe, text='Containers List', font=("Arial",14, "bold")).grid(column=2, row=2, sticky=W)
containersListBox = Listbox(mainframe, width=50)
containersListBox.grid(column=2, row=3)

# Container list button group
containerListButtonFrame = Frame(mainframe)
containerListButtonFrame.grid(column=2, row=4, sticky=(N, W, E, S))
ttk.Button(containerListButtonFrame, text='start', command=startContainer).grid(column=1, row=1, sticky=W)
ttk.Button(containerListButtonFrame, text='stop', command=stopContainer).grid(column=2, row=1, sticky=W)
ttk.Button(containerListButtonFrame, text='delete', command=removeContainer).grid(column=3, row=1, sticky=W)

# Add padding to all "children" (create border)
for child in mainframe.winfo_children():
  child.grid_configure(padx=10, pady=10)

# Pull initial data
getContainerList()
getImageList()

root.mainloop()
