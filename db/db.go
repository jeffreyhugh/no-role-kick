package db

import (
	"time"

	"github.com/qbxt/gologger"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type User struct {
	gorm.Model
	UserID    string    `gorm:"column:user_id"`
	GuildID   string    `gorm:"column:guild_id"`
	KickAt    time.Time `gorm:"column:kick_at"`
	Completed bool      `gorm:"column:completed"` // if there was an attempt to kick the user (prevents redundant API calls)
	Kicked    bool      `gorm:"column:kicked"`    // whether the user was actually kicked
}

var DB *gorm.DB

func Init() {
	// initialize sqlite connection
	var err error
	DB, err = gorm.Open(sqlite.Open("db.sqlite"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		gologger.Error("Failed to connect to database", err, nil)
	}

	// migrate tables
	DB.AutoMigrate(&User{})
	gologger.Info("Migrated tables", nil)
}
