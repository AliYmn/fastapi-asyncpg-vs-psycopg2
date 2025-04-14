# 🚀 App Service Makefile
# Modern and easy-to-understand build automation

#-----------------------------------------------
# 🐳 Docker Commands - Local Environment
#-----------------------------------------------

# 🏗️ Build all containers for local development
build:
	docker compose -f docker-compose.yml build

# 🚀 Start all services in detached mode for local development
up:
	docker compose -f docker-compose.yml up -d

# 🛑 Stop and remove all containers for local development
down:
	docker compose -f docker-compose.yml down

# ⏹️ Stop all services without removing them for local development
stop:
	docker compose -f docker-compose.yml stop

# 🔄 Restart all services for local development
restart:
	docker compose -f docker-compose.yml restart

#-----------------------------------------------
# 📊 Logging & Debugging
#-----------------------------------------------

# 📝 View logs for a specific service
log:
	docker compose logs -f app

# 🖥️ Open a bash shell in a container
bash:
	docker compose exec app bash

# 🐞 Run a service in debug mode with ports exposed
run-debug:
	docker compose stop app; \
	docker compose rm -f app; \
	docker compose run --rm --service-ports app

#-----------------------------------------------
# 🗄️ Database Migration Commands
#-----------------------------------------------

# 📝 Create a new migration
makemigrations:
	@echo '✏️ Migration Name: '; \
	read NAME; \
	docker compose run --rm app alembic -c /app/alembic.ini revision --autogenerate -m "$$NAME"

# ⬆️ Apply all migrations
migrate:
	docker compose run --rm app alembic -c /app/alembic.ini upgrade head

# 📋 Show migration history
showmigrations:
	docker compose run --rm app alembic -c /app/alembic.ini history

# 🏁 Initialize migrations
initmigrations:
	docker compose run --rm app alembic -c /app/alembic.ini init migrations

# ⬇️ Downgrade to a previous migration
downgrade:
	@echo '⏮️ Enter revision (or press enter for -1): '; \
	read REVISION; \
	if [ -z "$$REVISION" ]; then \
		docker compose run --rm app alembic -c /app/alembic.ini downgrade -1; \
	else \
		docker compose run --rm app alembic -c /app/alembic.ini downgrade $$REVISION; \
	fi
