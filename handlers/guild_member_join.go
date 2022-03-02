package handlers

import (
	"os"
	"strconv"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/qbxt/gologger"
	"github.com/sirupsen/logrus"
	"queue.bot/no-role-kick/db"
)

func GuildMemberJoin(s *discordgo.Session, g *discordgo.GuildMemberAdd) {
	kickTimeSeconds, err := strconv.ParseInt(os.Getenv("NRK_KICK_TIME"), 10, 64)
	if err != nil {
		gologger.Error("Could not parse kick time", err, nil)
		return
	}
	row := &db.User{
		UserID:    g.User.ID,
		GuildID:   g.GuildID,
		KickAt:    time.Now().Add(time.Duration(kickTimeSeconds) * time.Second),
		Completed: false,
	}
	if err := db.DB.Create(row).Error; err != nil {
		gologger.Error("Could not save new user in DB", err, nil)
		return
	}

	gologger.Info("User joined guild", logrus.Fields{
		"userID":  g.User.ID,
		"guildID": g.GuildID,
		"kickAt":  row.KickAt,
	})
}
