# NextPCB

### Get PCB quotations within KiCad and order with a single click

NextPCB plugin will help you:

- Extract key manufacturing parameters from your design
- Get real-time quotations from NextPCB within KiCad
- Generate Gerber files and upload them to NextPCB along with your personal board settings

Once the upload is complete, you can use the HQ DFM Gerber Viewer to double check your manufacturing files, adjust board parameters then add it to your NextPCB cart directly.
![NextPCB Plugin](https://github.com/SYSUeric66/kicad-amf-plugin/blob/8318782634b7f8237bd4a650c37e4031e876e3a0/docs/amf.gif)

## Features

### Automatic parameter extraction

When launching the plugin, the following parameters will be extracted from your KiCad design:

- Layer count
- Board size (x,y)
- Board thickness
- Minimum trace width/spacing
- Minimum drill hole size

_Note: These parameters cannot be edited from the plugin as they are extracted directly from your KiCad design._

### Real-time quotations completely within KiCad

Click the "Update Price" button to get the latest pricing and lead time for your boards from NextPCB.

You can modify other parameters (E.g. solder mask color, board quantity, etc.) at any time and re-quote the price with a click of a button. All the options are synced with [NextPCB](https://www.nextpcb.com/).

_Note: Some combinations are restricted (E.g. white silkscreen cannot be chosen with white solder mask)._

### One-click Gerber generation and sync to the order page

Click the "Place Order" button to generate Gerber and NC drill files and upload them straight to NextPCB's order page along with your board parameters.

Everything is in sync, so no additional adjustments are required. Of course, you are free to change the settings on the website and then proceed to order.

The following regions are supported:

- Europe and the U.S.A : [NextPCB](https://www.nextpcb.com/pcb-quote)
- Japan:[JP.NextPCB](https://jp.nextpcb.com/pcb-quote#/pcb-quote/)

## Installation

Download the latest release ZIP file from **reserved for package** then within KiCad, open the "Plugin and Content Manager" from the main window. Finally, install the ZIP file using "Install from File..." at the bottom of the window.
![image](https://github.com/HubertHQH/HQ-NextPCB/assets/125419974/97ef0ca3-380e-4f6f-a14b-6960271118fc)

## HQ PCB

HQ PCB is the China version of HQ PCB, supporting orders in China mainland.
- China mainland [HQPCB](https://www.hqpcb.com/quote/)

## HQ DFM

HQ DFM One-click analysis of over 20 design risk issues including open circuits, disconnected traces, line spacing, and width.
[华秋DFM](https://dfm.hqpcb.com/)
you can use the HQ DFM Gerber Viewer to double check your manufacturing files, adjust board parameters 

### About NextPCB

NextPCB specializes in reliable multilayer PCB manufacture and assembly, and like KiCad, our goal is to enable engineers to build tomorrow's electronics. NextPCB is working with KiCad to provide smart tools to simplify the progression from design to physical product. With 3 major factories catering to prototyping, mass production and PCB assembly, and over 15 years of engineering expertise, NextPCB believes our industrial experience will prove invaluable to KiCad users and the PCB design community.

We are a [KiCad Platinum Sponsor](https://www.nextpcb.com/blog/kicad-nextpcb-platinum-sponsorship).



## kicad-HQ install

### Windows

The Windows installation package can be downloaded directly using the following link:
https://www.eda.cn/data/kicad-release/kicad-huaqiu-8.0.6-x86_64.exe.zip

### Linux
The Linux version requires Flatpak installation

#### 1，Install flatpak

`sudo apt install flatpak`

#### 2，Map a domain name to a specific IP address

`sudo vim /etc/hosts`

Use vim to go to etc/host and add this line：
`175.6.14.183 kicad.huaqiu.com`

Check whether the connection is successful:
`ping kicad.huaqiu.com`

#### 3，Add a remote kicad repository

`flatpak remote-add --user repo https://kicad.huaqiu.com/kicadhuaqiu`

Check whether the addition succeeds：
`flatpak remote-ls repo`

If GPG verification is reported, go to Step 4. Otherwise, skip it

#### 4，Ignore package unsigned authentication and modify the configuration with the vim editor

`vim ~/.local/share/flatpak/repo/config`

Modify in the file:
`gpg-verify=false`

`flatpak remote-modify --no-gpg-verify repo`

Check whether the addition is successful:
`flatpak remote-ls repo`

#### 5，Install kicad

`flatpak install repo org.kicad.KiCad`

If no dependency is reported, go to the next step "6".

#### 6，Lack of SDK dependency, use domestic flathub mirror warehouse, add remote warehouse first, and then install the missing dependency:

`sudo flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub`

In case of lack org.freedesktop.Sdk/x86_64/23.08：
`flatpak install flathub org.freedesktop.Sdk/x86_64/23.08`

In case of lack org.freedesktop.Sdk//23.08：
`flatpak install flathub org.freedesktop.Sdk//23.08`
