terraform {
  required_version = ">= 1.6"
  required_providers {
    hcloud = { source = "hetznercloud/hcloud", version = "~> 1.49" }
  }
  backend "http" {} # état stocké dans GitLab (configuré par le pipeline)
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_ssh_key" "deploy" {
  name       = "${var.name}-deploy"
  public_key = var.ssh_public_key
}

resource "hcloud_server" "app" {
  name         = var.name
  image        = "ubuntu-24.04"
  server_type  = var.server_type
  location     = var.location
  ssh_keys     = [hcloud_ssh_key.deploy.id]
  firewall_ids = [hcloud_firewall.web.id]
  labels       = { course = "devops", app = "biblio" }
}
