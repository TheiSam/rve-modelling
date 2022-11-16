import matplotlib.pyplot as plt


############ THIS FILE CONTAINS A FUNCTION TO DRAW CIRCLES ON AN IMAGE ##############

# Function for drawing circles
def draw(image,circles,title):
    fig = plt.figure(figsize=(5, 5)) # fig, ax = plt.subplots()
    plt.suptitle(title, fontsize=35)
    plt.imshow(image, cmap='gray', vmin=0, vmax=255);
    for row in circles[0, :]:
     # draw the outer circle
     fig = plt.gcf();
     ax = fig.gca()
     circle = plt.Circle((row[0], row[1]), row[2], color='r', linewidth = 2, fill=False, clip_on = True)
     ax.add_artist(circle)
     plt.axis('off');
     plt.axis('equal'); plt.show(block=False);


