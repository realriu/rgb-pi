{
    "commands":[
        {
            "type":"loop",
            "condition":"{b:1}",
            "commands":
            [
               {
                    "type":"fade",
                    "time":"5",
                    "end":"{r:0-1,0-0,0-0}"
                },
                {
                    "type":"fade",
                    "time":"1.5",
                    "end":"{r:0-0,0-0,0-1}"
                },

                {
                    "type":"fade",
                    "time":"10",
                    "end":"{r:0-0,0-1,0-0}"
                }
            ]
        }
    ]
}

