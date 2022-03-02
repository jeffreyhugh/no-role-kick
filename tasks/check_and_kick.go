package tasks

import (
	"fmt"
	"os"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/qbxt/gologger"
	"github.com/sirupsen/logrus"
	"queue.bot/no-role-kick/db"
)

func CheckAndKick(s *discordgo.Session) {
	rows := make([]*db.User, 0)
	if err := db.DB.Where("kick_at < ? AND NOT completed", time.Now()).Find(&rows).Error; err != nil {
		gologger.Error("Could not get users from DB", err, nil)
		return
	}

	for _, row := range rows {
		row.Completed = true
		err := s.GuildMemberDeleteWithReason(row.GuildID, row.UserID, fmt.Sprintf("%s did not have a role after %s seconds", row.UserID, os.Getenv("NRK_KICK_TIME")))
		if err != nil {
			gologger.Error("Could not kick user", err, logrus.Fields{
				"userID":  row.UserID,
				"guildID": row.GuildID,
			})
			return
		}
		row.Kicked = true
		gologger.Info("Kicked user", logrus.Fields{
			"userID":  row.UserID,
			"guildID": row.GuildID,
		})
	}

	if len(rows) > 0 {
		if err := db.DB.Save(&rows).Error; err != nil {
			gologger.Error("Could not save kicked users in DB", err, nil)
			return
		}
	}
}
