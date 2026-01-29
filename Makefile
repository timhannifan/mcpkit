.DEFAULT_GOAL := help

# Deploy branch (defaults to main)
BRANCH ?= main

.PHONY: dev dev-down prod prod-down seed-db deploy clean logs restart-mcp help

dev: ## Start local development (http://localhost:3000)
	docker-compose up -d

dev-down: ## Stop local development
	docker-compose down

prod: ## Start production services (with Caddy reverse proxy)
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

prod-down: ## Stop production services
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml down

seed-db: ## Seed the Neo4j citation demo (run after make dev; runs script in mcp-server container)
	docker-compose run --rm \
		-v $(PWD)/scripts:/scripts \
		-w /scripts \
		-e NEO4J_URI=bolt://neo4j:7687 \
		-e NEO4J_USER=neo4j \
		-e NEO4J_PASSWORD=$${NEO4J_PASSWORD:-password123} \
		mcp-server python neo4j_citation_demo.py

logs: ## View MCP server logs (usage: make logs or make logs SERVICE=mcp-server)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f mcp-server; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

restart-mcp: ## Restart the MCP server container (e.g. after code changes)
	docker-compose restart mcp-server

deploy: ## Deploy to EC2 (usage: make deploy BRANCH=main)
	./scripts/deploy.sh $(BRANCH)

clean: ## Clean up Docker images and containers
	docker-compose down --rmi all --volumes --remove-orphans
	docker image prune -f

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@echo "  Development:"
	@echo "    dev             Start local development (http://localhost:3000)"
	@echo "    dev-down        Stop local development"
	@echo "    seed-db         Seed the Neo4j citation demo (run after make dev)"
	@echo "    logs            View MCP server logs (make logs or make logs SERVICE=name)"
	@echo "    restart-mcp     Restart the MCP server container"
	@echo ""
	@echo "  Production:"
	@echo "    prod            Start production services (with Caddy reverse proxy)"
	@echo "    prod-down       Stop production services"
	@echo "    deploy          Deploy to EC2 (make deploy BRANCH=main)"
	@echo ""
	@echo "  Other:"
	@echo "    clean           Clean up Docker images and containers"
	@echo ""
