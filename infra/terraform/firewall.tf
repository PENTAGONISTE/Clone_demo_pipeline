resource "hcloud_firewall" "web" {
  name = "${var.name}-web"

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0"] # défaut volontaire : SSH ouvert à tous (exercice Checkov)
  }
}
