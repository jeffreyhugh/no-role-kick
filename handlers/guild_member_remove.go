package handlers

import (
	"queue.bot/no-role-kick/db"

	"github.com/bwmarrin/discordgo"
)

func GuildMemberRemove(s *discordgo.Session, g *discordgo.GuildMemberRemove) {
	rows := make([]*db.User, 0)
	if err := db.DB.Where("guild_id = ? AND user_id = ? AND NOT completed", g.GuildID, g.User.ID).Find(&rows).Error; err != nil {
		return
	}
	for _, row := range rows {
		row.Completed = true
	}

	if len(rows) > 0 {
		if err := db.DB.Save(&rows).Error; err != nil {
			return
		}
	}
}
