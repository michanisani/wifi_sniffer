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
# 0.3 27-10-2023
# 0.4 add free memory

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

# Initial table size
num_rows = 19
num_cols = 5    
temperature = ' '
weather_description = ' '


# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
orange = (255,200,0)
bg = (204, 102, 0)


# Initialize button positions
exit_label_X_pos = screen_width - 55 #735
exit_label_Y_pos = screen_height - 476 #4
next_label_X_pos = screen_width - 130 # 670
next_label_Y_pos = screen_height - 476 # 4
cell_width = screen_width // 6
cell_height = screen_height // 19
table_x = 0
table_y = 10

cell_width_B = screen_width // 12
cell_height_B = screen_height // 19

exit_button = pygame.Rect(exit_label_X_pos, exit_label_Y_pos, cell_width_B, cell_height_B)
next_button = pygame.Rect(next_label_X_pos, next_label_Y_pos, cell_width_B, cell_height_B)

last_update_time_table = 0
last_update_time_net = 0
last_update_time_bar = 0

Start_To_Scan = 1 # start scan
Scan_Result_Plist=[]

#-----------------------------------------------------------------------------------
def search_net():
    global Start_To_Scan
    global Scan_Result_Plist
    NO_OF_LINES_TO_PRINT = 15

    if (Start_To_Scan == 1):
        print("Start To Scan Net")
        screen.fill(pygame.Color("black"))
        #text_font = pygame.font.SysFont("Helvetica", 18)
        text_font = pygame.font.Font(None, 18)
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
                        print(f"IP: {current_ip}     MAC: {mac_address}     Name:{device_name}")
        # Get the contents of the StringIO object as a string
        output_string = string_buffer.getvalue()
        # Close the StringIO object
        string_buffer.close()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        Scan_Result_Plist = output_string.splitlines()
        Plist_len = len (Scan_Result_Plist)
        print("Plist Len=", Plist_len)
        
    print_next_lines(Scan_Result_Plist, NO_OF_LINES_TO_PRINT)
        
        
#-----------------------------------------------------------------------------------------------------------------
'''
# Example usage:
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6"]
print_next_lines(lines, 2)  # Prints the first 2 lines
print_next_lines(lines, 2)  # Prints the next 2 lines
print_next_lines(lines, 3)  # Prints the remaining lines (3 and 4)
print_next_lines(lines, 2)  # Prints "All lines have been printed."
'''
def print_next_lines(lines, A):
    global Start_To_Scan
    ltop=[]
    
    if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines) or not isinstance(A, int):
        print("Invalid input. 'lines' should be a list of strings, and 'A' should be an integer.")
        return
    if A <= 0:
        print("A should be a positive integer.")
        return
    if not hasattr(print_next_lines, 'current_index'):
        print_next_lines.current_index = 0
    current_index = print_next_lines.current_index
    if current_index >= len(lines):
        print("All lines have been printed.")
        print_next_lines.current_index = 0
        Start_To_Scan = 1 # start scan
        return   # scan next time from begining
    else:
        for i in range(current_index, min(current_index + A, len(lines))):
            print(lines[i])
            ltop.append(lines[i])
        print_next_lines.current_index = min(current_index + A, len(lines))
        display_formatted_text(ltop,10,10,780,460)
        Start_To_Scan = 0 # do not scan
        return  # do not scan
#----------------------------------------------------------------------------------------------
#function for outputting text onto the screen
def draw_text(text,x,y, text_col):
    global font
    text_font = pygame.font.SysFont("Helvetica", 18)
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
#--------------------------------------------------------------------------------------------------
# Function to display formatted text on the screen
def display_formatted_text(text, x, y, width, height, font_size=28, line_spacing=1):
    font = pygame.font.Font(None, font_size)
        
    #lines = text.split("\n")  # Split the text into lines based on newline characters
    lines = text
    screen.fill(pygame.Color("black")) # erases the entire screen surface
    y_offset = y
    for line in lines:
        if "Unknown" in line:
            text_surface = font.render(line, True, red)
        else:
            text_surface = font.render(line, True, white)
        screen.blit(text_surface, (x, y_offset))
        y_offset += font_size + line_spacing

    pygame.display.flip()


#-----------------------------------------------------------------------------------
def draw_buttons():
    pygame.draw.rect(screen, red, exit_button)
    pygame.draw.rect(screen, green, next_button)
    font = pygame.font.Font(None, 28)
    exit_text = font.render("Exit", True, white)
    next_text = font.render("Next", True, white)
    screen.blit(exit_text, (exit_label_X_pos, exit_label_Y_pos))
    screen.blit(next_text, (next_label_X_pos, next_label_Y_pos))

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
#------------------------------------------------------------------------------------------------------------
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
# Function to scan and list nearby access points
unique_combinations = set()
unique_cells = []
scan_counter = 0
def list_access_points():
    global scan_counter,unique_cells,unique_combinations
    
    try:
        cells = wifi.Cell.all('wlan0')
    except:
        SendData("WiFi list AP fail")
        return []
#    return cells # cell object

    # Deduplicate the scan results based on SSID,freq,channel,address
    # Initialize a set to store unique scan result combinations
    # Create a set of unique scan result combinations
    scan_counter += 1
    if (scan_counter > 8):
        unique_cells.clear()
        unique_combinations.clear()
        scan_counter = 0
        
    for cell in cells:
        combination = (cell.ssid, cell.frequency, cell.channel, cell.address)
        if combination not in unique_combinations:
            unique_combinations.add(combination)
            unique_cells.append(cell)
    return unique_cells
 

 
#------------------------------------------------------------
# Define a function to draw the table
def draw_table(cols, rows):
    global screen_width , screen_height
    global cell_width, cell_height           # 7 19

    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, white, (table_x + col * cell_width, table_y + row * cell_height, cell_width, cell_height), 1)
            
# Define a function to draw text in a specific cell
#draw_text(text,x,y, text_col):
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
    screen.fill(pygame.Color("black")) # erases the entire screen surface
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

    temperature_label_position = (screen_width - 350, screen_height - 470) # 450
    description_label_position = (screen_width - 600, screen_height - 470) # 435
    screen.blit(temperature_text_surface, temperature_label_position)
    screen.blit(description_text_surface, description_label_position)
    # amount of free RAM
    '''
    free_memory = get_free_memory()
    freemem_label = f"Free mem={free_memory}"
    freemem_text_surface = font.render(freemem_label, True, (255,200,0))
    freemem_label_position = (screen_width - 175, screen_height - 400) 
    screen.blit(freemem_text_surface, freemem_label_position)
    '''

    #print(f"Free memory on Raspberry Pi: {free_memory} kB")

 
#----------------------------------------------------
def display_bars():
    update_interval_bar = 10 # Update the display every 10 seconds
    global last_update_time_bar
    cells = []  # Store the access points data

    current_time = time.time()
    if (current_time - last_update_time_bar) >= update_interval_bar:
        # Get the list of nearby access points
        cells = list_access_points()
        temperature, weather_description = get_weather()
        last_update_time_bar = current_time
        # Draw the stored access points data
        if cells:
        # Clear the screen
            print("displae bars")
            screen.fill(pygame.Color("black")) # erases the entire screen surface
            draw_signal_bars(cells,temperature,weather_description)


#---------------------------------------------------------------------------------
def display_table():
    update_interval_dis = 10  # Update the display every 10 seconds
    global last_update_time_table
    cells = []  # Store the access points data

    current_time = time.time()
    if current_time - last_update_time_table >= update_interval_dis:
                cells = list_access_points()
                last_update_time_table = current_time
                if cells:
                    print("# Draw your table here")
                    Clear_Table(num_cols, num_rows)
                    Count_Colon = 0
                    Count_Row = 1  # start from 2'd
                    for cell in cells:
                        signal_strength = cell.signal
                        ssid = cell.ssid
                        channel = cell.channel
                        frequency = cell.frequency
                        signal_quality = cell.quality
                        draw_text(str(channel), Count_Colon, Count_Row, white)
                        draw_text(str(frequency), Count_Colon + 1, Count_Row, white)
                        draw_text(str(signal_strength), Count_Colon + 2, Count_Row, white)
                        draw_text(str(signal_quality), Count_Colon + 3, Count_Row, white)
                        draw_text(str(ssid), Count_Colon + 4, Count_Row, white)
                        Count_Row = Count_Row + 1
#--------------------------------------------------------------------------------------
def display_search_net():

    update_interval_net = 15  # Update the display every 10 seconds
    global last_update_time_net

    current_time = time.time()
    if current_time - last_update_time_net >= update_interval_net:
        search_net()
        last_update_time_net = current_time 
                
                
#------------------------------------------------------------------------------------------------
def get_free_memory():
    with open('/proc/meminfo', 'r') as meminfo:
        for line in meminfo:
            if 'MemFree' in line:
                free_memory = int(line.split()[1])
                return free_memory

#---------------------------------------------------------------------------------------
def main():
    state = 0
    exit_clicked = False
    next_clicked = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if exit_button.collidepoint(event.pos):
                        exit_clicked = True
                    if next_button.collidepoint(event.pos):
                        next_clicked = True

        if exit_clicked:
            running = False
        elif next_clicked:
            state += 1
            next_clicked = False
            screen.fill(pygame.Color("black")) # erases the entire screen surface
            font = pygame.font.Font(None, 44)
            text_surface = font.render("Scan_NET....", True, red)
            screen.blit(text_surface, (320, 190))
            pygame.display.update()
            print("Erase Screen")
            if (state > 2) :
                state =0

        if state == 0:
            display_bars()
            draw_buttons()
        elif state == 1:
            # Table mode
            display_table()
            draw_buttons()
        elif state == 2:
            # Search net mode
            display_search_net()
            draw_buttons()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()


