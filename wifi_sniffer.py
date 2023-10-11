#Each cell object should have the following attributes:
#• ssid
#• signal
#• quality
#• frequency
#• bitrates
#• encrypted
#• channel
#• address
#• mode
#For cells that have encrypted as True, there will also be the following attributes:
#• encryption_type

#You can also use the wifi.scan_networks() method to scan for APs. This method returns a dictionary of APs, where the key is the BSSID of the AP and the value is a Cell object. The scan_networks() method does not have a scan_timeout parameter, so it will scan for APs until it has found all of them.
#Here is an example of how to use the wifi.scan_networks() method:
#aps = wifi.scan_networks('wlan0')
#for bssid, cell in aps.items():
#    print(cell.ssid, cell.bssid, cell.channel, cell.signal)
# ssh 10.0.0.203 pw:m559n233

# Versions
# 0.1 - 24 sep 2023
# 0.2 - read device name on the net- using search_net()

import os
from io import StringIO
import sys
import wifi
import pygame
from pygame.locals import *
import time
import random
import requests
import subprocess
import re
"""

@@@@@@@ windows wifi only

import subprocess
# getting meta data of the wifi network
meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])
# decoding meta data from byte to string
data = meta_data.decode('utf-8', errors ="backslashreplace")
# splitting data by line by line
# string to list
data = data.split('\n')
# creating a list of wifi names
names = []
# traverse the list
for i in data:
    # find "All User Profile" in each item
    # as this item will have the wifi name
    if "All User Profile" in i :
        # if found split the item
        # in order to get only the name
        i = i.split(":")
        # item at index 1 will be the wifi name
        i = i[1]
        # formatting the name
        # first and last character is use less
        i = i[1:-1]
        # appending the wifi name in the list
        names.append(i)
# printing the wifi names
print("All wifi that system has connected to are ")
print("-----------------------------------------")
for name in names:
    print(name)

@@@@@@@@@@@@@@@
"""




# Initialize pygame
# Set the SDL_VIDEODRIVER environment variable to "dummy"
#os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
os.environ["DISPLAY"] = ":0" # for run LCD in SSH terminal
pygame.display.init()
pygame.font.init()

# Initialize the font here
font = pygame.font.Font(None, 12)  #36 You can adjust the font size as needed



# Set the screen dimensions to match your touchscreen resolution
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Full-screen mode
#screen = pygame.display.set_mode((800, 480)) # 800X480

# Get the screen dimensions
screen_width, screen_height = pygame.display.get_surface().get_size()
print(screen_width,screen_height)
#pygame.mouse.set_visible(False)  # Hide the cursor

#---global variable ------------------
exit_label_X_pos = screen_width - 55 #735
exit_label_Y_pos = screen_height - 476 #4
table_label_X_pos = screen_width - 130 # 670
table_label_Y_pos = screen_height - 476 # 4
cell_width = screen_width // 6
cell_height = screen_height // 19
table_x = 0
table_y = 10
# Initial table size
num_rows = 19
num_cols = 5    
temperature = ' '
weather_description = ' '
#define global variable
clicked = False


# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
orange = (255,200,0)
bg = (204, 102, 0)

#-----------------------------------------------------------------------------------
def search_net():
    # Create a StringIO object to capture the printed output
    string_buffer = StringIO()
    # Redirect the standard output to the StringIO object
    sys.stdout = string_buffer

    # Define the nmap command with $(which nmap) to ensure it's in the PATH
    nmap_command = ['sudo', '$(which nmap)', '-sn', '10.0.0.0/24']
    # Run the nmap command using subprocess
    nmap = subprocess.Popen(' '.join(nmap_command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the process to finish and collect its output
    output, error = nmap.communicate()
    # Check for errors, if any
    if nmap.returncode != 0:
        print("An error occurred while running nmap:")
        print(error.decode('utf-8'))
    else:
        # Process the output to extract and print IP addresses, MAC addresses, and device names
        lines = output.decode('utf-8').splitlines()
        current_ip = ""
        for line in lines:
            # Check if the line contains an IP address
            ip_match = re.search(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                current_ip = ip_match.group(1)
            else:
                # Use regular expressions to match and extract MAC addresses and device names
                mac_match = re.search(r'MAC Address: ([0-9A-Fa-f:]+) \((.+)\)', line)
                if mac_match:
                    mac_address = mac_match.group(1)
                    device_name = mac_match.group(2)
                    print(f"IP:{current_ip}, MAC:{mac_address},Name:{device_name}")
                    
                    
    # Get the contents of the StringIO object as a string
    output_string = string_buffer.getvalue()
    # Close the StringIO object
    string_buffer.close()
    # Reset the standard output
    sys.stdout = sys.__stdout__
    print(output_string)
    display_formatted_text(output_string,0,0,800,480)
    
#----------------------------------------------------------------------------------------------

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    text_font = pygame.font.SysFont("Helvetica", 24)
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to display formatted text on the screen
def display_formatted_text(text, x, y, width, height, font_size=24, line_spacing=5):
    font = pygame.font.Font(None, font_size)
    lines = []
    remaining_text = text

    screen.fill(white)
    while remaining_text:
        line = ""
        while len(remaining_text) > 0:
            line_size = font.size(line + remaining_text[0])
            if line_size[0] < width:  # Corrected this line
                line += remaining_text[0]
                remaining_text = remaining_text[1:]
            else:
                break
        lines.append(line)

    max_lines = height // (font_size + line_spacing)
    lines = lines[:max_lines]  # Only display as many lines as fit on the screen

    y_offset = y
    for line in lines:
        text_surface = font.render(line, True, black)
        screen.blit(text_surface, (x, y_offset))
        y_offset += font_size + line_spacing

    pygame.display.flip()

#-----------------------------------------------------------------------------------
class button():
        
    #colours for button and text
    button_col = (255, 0, 0)
    hover_col = (75, 225, 255)
    click_col = (50, 150, 255)
    text_col = black
    bwidth = 60 #180
    bheight = 40 #70

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw_button(self):
        global clicked
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        #create pygame Rect object for the button
        button_rect = Rect(self.x, self.y, self.bwidth, self.bheight)
        #check mouseover and clicked conditions
        if button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
                pygame.draw.rect(screen, self.click_col, button_rect)
            elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
                clicked = False
                action = True
            else:
                pygame.draw.rect(screen, self.hover_col, button_rect)
        else:
            pygame.draw.rect(screen, self.button_col, button_rect)
        #add shading to button
        pygame.draw.line(screen, white, (self.x, self.y), (self.x + self.bwidth, self.y), 2)
        pygame.draw.line(screen, white, (self.x, self.y), (self.x, self.y + self.bheight), 2)
        pygame.draw.line(screen, black, (self.x, self.y + self.bheight), (self.x + self.bwidth, self.y + self.bheight), 2)
        pygame.draw.line(screen, black, (self.x + self.bwidth, self.y), (self.x + self.bwidth, self.y + self.bheight), 2)
        
        font = pygame.font.Font(None,32)
        text_img = font.render(self.text, True, self.text_col)
        text_len = text_img.get_width()
        screen.blit(text_img, (self.x + int(self.bwidth / 2) - int(text_len / 2), self.y + 15)) #25
        return action

#------------------------------------------------------------------------------------
# Function to fetch weather data from OpenWeatherMap API
def get_weather():
    global temperature,weather_description
    
    city = 'Hod Hasharon'
    country_code = 'IL'
    API_KEY = 'a495a627e4daf53f77409213800bf92f'  # michanisani@gmail.com m559n233 API key
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={API_KEY}&units=metric'
    response = requests.get(base_url)
    data = response.json()
    # Extract relevant weather information
    temperature = data['main']['temp']
    weather_description = data['weather'][0]['description']
    return temperature, weather_description

# Function to scan and list nearby access points
def list_access_points():
     cells = wifi.Cell.all('wlan0')
     return cells
#------------------------------------------------------------
# Define a function to draw the table
def draw_table(cols, rows):
    global cell_width, cell_height
    global screen_width , screen_height
    
    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, black, (table_x + col * cell_width, table_y + row * cell_height, cell_width, cell_height), 1)
            
# Define a function to draw text in a specific cell
def draw_text(text, col, row,color):
    global cell_width, cell_height
    global screen_width , screen_height
    global table_x , table_y
    
    FONT_SIZE = 26
    font = pygame.font.Font(None, FONT_SIZE)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (table_x + (col * cell_width) + (cell_width//2) ,table_y+ (row * cell_height) + (cell_height//2))
    screen.blit(text_surface, text_rect)

def Clear_Table(num_cols,num_rows):
    screen.fill(pygame.Color("white")) # erases the entire screen surface
    draw_table(num_cols, num_rows)
    # print table first line
    draw_text("CHA",  0, 0,orange)
    draw_text("FREQ", 1, 0,orange)
    draw_text("RSSI", 2, 0,orange)
    draw_text("QUALITY", 3, 0,orange)
    draw_text("SSID", 4, 0,orange)

#----------------------------------------------------------------------------------------------------------------
# Function to draw signal strength bars and labels on the screen
def draw_signal_bars(cells,temperature, weather_description):
    max_strength = -20  # Maximum signal strength in dBm
    min_strength = -100  # Minimum signal strength in dBm
    bar_width = 15
    space_between_bars = 90
    x_offset = 0
    # this cmd stack rasbery pi
    #AP_counter = len(cells)
    #if AP_counter > 6:
        #space_between_bars = int((screen_width - bar_width*AP_counter) / AP_counter)
    for cell in cells:
        signal_strength = cell.signal
        ssid = cell.ssid
        channel = cell.channel
        frequency = cell.frequency
        bar_height = (signal_strength - min_strength) / (max_strength - min_strength) * (screen_height - 40)
        #print(signal_strength,channel,frequency)
        # Generate a random color for each bar
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        # Display the title
        font = pygame.font.Font(None, 20)
        # Display the channel value below the RSSI label
        channel_label = "Ch: " + str(channel)
        channel_text_surface = font.render(channel_label, True, white)
        channel_label_position = (x_offset, screen_height - 40 - bar_height)
        screen.blit(channel_text_surface, channel_label_position)

        # Display the signal strength value above the bar
        strength_label = "RSSI: " + str(signal_strength) + " dBm"
        strength_text_surface = font.render(strength_label, True,white )
        strength_label_position = (x_offset, screen_height - 60 - bar_height)
        screen.blit(strength_text_surface, strength_label_position)

        # Display the SSID value above the bar
        ssid_label = "SSID: " + ssid
        ssid_text_surface = font.render(ssid_label, True, white)
        ssid_label_position = (x_offset, screen_height - 80 - bar_height)
        screen.blit(ssid_text_surface, ssid_label_position)

        # Display the freq value above the bar
        freq_label = "Freq: " + frequency
        freq_text_surface = font.render(freq_label, True, white)
        freq_label_position = (x_offset, screen_height - 100 - bar_height)
        screen.blit(freq_text_surface, freq_label_position)

        pygame.draw.rect(screen, color, (x_offset, screen_height - 20 - bar_height, bar_width, bar_height))
        x_offset += bar_width + space_between_bars

    temperature_label = f"Temperature: {temperature}°C"
    description_label = f"Weather: {weather_description}"
    font = pygame.font.Font(None, 24)
    temperature_text_surface = font.render(temperature_label, True, (255,200,0))
    description_text_surface = font.render(description_label, True, (255,200,0))

    temperature_label_position = (screen_width - 175, screen_height - 390) # 450
    description_label_position = (screen_width - 175, screen_height - 375) # 435
    screen.blit(temperature_text_surface, temperature_label_position)
    screen.blit(description_text_surface, description_label_position)
    
# Function to draw the exit button
def draw_exit_button():
    global exit_label_X_pos, exit_label_Y_pos

    font = pygame.font.Font(None, 36)
    exit_label = "Exit"
    exit_text_surface = font.render(exit_label, True, (255,0,0))
    exit_label_position = (exit_label_X_pos, exit_label_Y_pos)
    screen.blit(exit_text_surface, exit_label_position)
    
# Function to draw the exit button
def draw_table_button():
    global table_label_X_pos,table_label_Y_pos

    font = pygame.font.Font(None, 36)
    table_label = "Table"
    table_text_surface = font.render(table_label, True, (255,0,0))
    table_label_position = (table_label_X_pos,table_label_Y_pos)
    screen.blit(table_text_surface, table_label_position)
  

def main():
    global exit_label_X_pos, exit_label_Y_pos
    global table_label_X_pos,table_label_Y_pos
    global temperature,weather_description
    global num_rows,num_cols
    
    pygame.display.set_caption("Wi-Fi Signal Strength Bars")
    update_interval = 10  # Update the display every 10 seconds
    last_update_time = 0
    cells = []  # Store the access points data

    running = True
    table = False
    first_time_table = 1
    OKto_search_net = False
    Table_B = button(675, 1, 'Table')
    Exit_B = button(735, 1, 'Exit')
    Search_Net = button (675,45,'NET')
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if Exit_B.draw_button():
            running = False
        if Table_B.draw_button():
            table = not table # togale
        if Search_Net.draw_button():
            OKto_search_net=True
            
        if (table == True) and (first_time_table == 1):
        # Draw the stored access points data
            # Clear the screen
            screen.fill(white)
            # Draw the table
            draw_table(num_cols,num_rows)
            first_time_table = 0
           
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            # Get the list of nearby access points
            cells = list_access_points()
            temperature, weather_description = get_weather()
            last_update_time = current_time
            if table == False:
                # Draw the stored access points data
                if cells:
                    # Clear the screen
                    screen.fill(black)
                    draw_signal_bars(cells,temperature,weather_description)
            if table == True:
                # Draw the stored access points data
                if cells:
                    Clear_Table(num_cols,num_rows)
                    Count_Colon = 0
                    Count_Row   = 1 # start from 2'd
                    # Add text to specific cells
                    # colon start from 0,1,2,3,
                    # row start from 0,1,2
                    for cell in cells:
                        signal_strength = cell.signal
                        ssid = cell.ssid
                        channel = cell.channel
                        frequency = cell.frequency
                        signal_quality = cell.quality
                        draw_text(str(channel), Count_Colon,Count_Row,black)  
                        draw_text(str(frequency), Count_Colon+1,Count_Row,black)  
                        draw_text(str(signal_strength), Count_Colon+2,Count_Row,black) 
                        draw_text(str(signal_quality), Count_Colon+3,Count_Row,black) 
                        draw_text(str(ssid), Count_Colon+4,Count_Row,black) 
                        Count_Row   = Count_Row + 1
                       
            if (OKto_search_net==True):
                search_net()
                OKto_search_net=False
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if the touch event occurred
                        touch_pos = pygame.mouse.get_pos()

        #draw_frequency_buttons(frequency_band)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
