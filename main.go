package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"queue.bot/no-role-kick/db"
	"queue.bot/no-role-kick/handlers"
	"queue.bot/no-role-kick/tasks"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
	"github.com/qbxt/gologger"
	"github.com/robfig/cron"
	"github.com/sirupsen/logrus"
)

func main() {
	godotenv.Load("nrk.env")

	logLevelString, ok := os.LookupEnv("NRK_LOG_LEVEL")
	if !ok {
		logLevelString = "info"
	}

	logLevel, err := logrus.ParseLevel(logLevelString)
	if err != nil {
		logLevel = logrus.InfoLevel
	}

	gologger.Init(logLevel)

	// db
	gologger.Info("Connecting to DB", nil)
	db.Init()
	gologger.Info("Connected to DB", nil)

	// discord
	gologger.Info("Initializing bot", nil)
	dg, err := discordgo.New(fmt.Sprintf("Bot %s", os.Getenv("NRK_DISCORD_TOKEN")))
	if err != nil {
		gologger.Fatal("Failed to initialize bot", err, nil)
	}

	dg.Identify.Intents = discordgo.IntentsGuildMembers

	dg.AddHandler(handlers.GuildMemberJoin)
	// if the user leaves and then rejoins, this "resets" the timer by marking the old row as completed
	dg.AddHandler(handlers.GuildMemberRemove)

	// cron
	gologger.Info("Starting cron", nil)
	c := cron.New()
	c.AddFunc(fmt.Sprintf("@every %ss", os.Getenv("NRK_DB_POLLING_FREQUENCY")), func() {
		tasks.CheckAndKick(dg)
	})
	c.Start()

	// run
	err = dg.Open()
	if err != nil {
		gologger.Fatal("Failed to open connection to Discord", err, logrus.Fields{
			"token": os.Getenv("NRK_DISCORD_TOKEN"),
		})
	}

	gologger.Info("Bot is running, press CTRL-C to exit", logrus.Fields{
		"userID": dg.State.User.ID,
	})

	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	gologger.Info("Received exit signal, shutting down", nil)

	dg.Close()
}
