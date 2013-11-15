﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Navigation;
using Microsoft.Phone.Controls;
using Microsoft.Phone.Shell;
using RGB.Resources;
using System.Threading;
using Coding4Fun.Toolkit.Controls;

namespace RGB
{
    public partial class MainPage : PhoneApplicationPage
    {
        private SocketClient client = new SocketClient();
        private Thread worker;

        private readonly Queue<RGBCommand> commandQ = new Queue<RGBCommand>();

        private enum RGBCommandType
        {
            ChangeColor = 1
        }

        private struct RGBCommand
        {
            public float R, G, B;
            public RGBCommandType Type;

            public RGBCommand(RGBCommandType type, float r, float g, float b)
            {
                Type = type;
                R = r;
                G = g;
                B = b;
            }
        }

        // Constructor
        public MainPage()
        {
            InitializeComponent();

            // Set the data context of the listbox control to the sample data
            DataContext = App.ViewModel;

            // Sample code to localize the ApplicationBar
            BuildLocalizedApplicationBar();

            ColorPicker colorPicker = new ColorPicker();
            colorPicker.ColorChanged += colorPicker_ColorChanged;
            gridChooseColor.Children.Add(colorPicker);

            worker = new Thread(rgbWorking);
            worker.IsBackground = true;
            worker.Start();

        }

        void colorPicker_ColorChanged(object sender, System.Windows.Media.Color color)
        {
            lock (commandQ)
            {
                if (commandQ.Count > 0) commandQ.Clear();
                commandQ.Enqueue(new RGBCommand(RGBCommandType.ChangeColor, color.R / 255.0f, color.G / 255.0f, color.B / 255.0f));
                Monitor.PulseAll(commandQ);
            }
        }


        private void rgbWorking()
        {
            while (true)
            {
                try
                {
                    RGBCommand c;
                    lock (commandQ)
                    {

                        while (commandQ.Count == 0)
                        {
                            Monitor.Wait(commandQ, 1000);
                        }


                        c = commandQ.Dequeue();
                    }


                    client.Connect("192.168.1.150", 4321);
                    client.Send(c.R.ToString("F3") + " " + c.G.ToString("F3") + " " + c.B.ToString("F3"));
                    client.Close();
                }
                catch { }
            }
        }


        // Load data for the ViewModel Items
        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
            if (!App.ViewModel.IsDataLoaded)
            {
                App.ViewModel.LoadData();
            }
        }



        // Sample code for building a localized ApplicationBar
        private void BuildLocalizedApplicationBar()
        {
            // Set the page's ApplicationBar to a new instance of ApplicationBar.
            ApplicationBar = new ApplicationBar();

            // Create a new button and set the text value to the localized string from AppResources.
            ApplicationBarIconButton abbOn = new ApplicationBarIconButton(new Uri("/Assets/Icons/on.png", UriKind.Relative));
            abbOn.Text = "On";
            abbOn.Click += delegate(object s, EventArgs ea)
            {
                System.Windows.Media.Color color = System.Windows.Media.Color.FromArgb(255, 255, 255, 255);
                client.Connect("192.168.1.150", 4321);
                client.Send((color.R / 255.0).ToString("F3") + " " + (color.G / 255.0).ToString("F3") + " " + (color.B / 255.0).ToString("F3"));
                client.Close();
            };
            ApplicationBar.Buttons.Add(abbOn);

            ApplicationBarIconButton abbOff = new ApplicationBarIconButton(new Uri("/Assets/Icons/off.png", UriKind.Relative));
            abbOff.Text = "Off";
            abbOff.Click += delegate(object s, EventArgs ea)
            {
                System.Windows.Media.Color color = System.Windows.Media.Color.FromArgb(255, 0, 0, 0);
                client.Connect("192.168.1.150", 4321);
                client.Send((color.R / 255.0).ToString("F3") + " " + (color.G / 255.0).ToString("F3") + " " + (color.B / 255.0).ToString("F3"));
                client.Close();
            };
            ApplicationBar.Buttons.Add(abbOff);

            // Create a new menu item with the localized string from AppResources.
            //ApplicationBarMenuItem appBarMenuItem = new ApplicationBarMenuItem(AppResources.AppBarMenuItemText);
            //ApplicationBar.MenuItems.Add(appBarMenuItem);
        }


    }
}