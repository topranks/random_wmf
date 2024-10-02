class whatever (
    # Additonal DNS metadata
    Hash[Stdlib::IP::Address, String] $dns_reverse_zones    = lookup('profile::netbox::dns_reverse_zones'),
    Hash                              $kubernetes_clusters  = lookup('kubernetes::clusters')  # lint:ignore:wmf_styleguide
) {


    # Reverse DNS zone data used by dns script
    file { '/etc/netbox/dns_reverse_zones.yaml':
        owner   => 'netbox',
        group   => 'www-data',
        mode    => '0400',
        content => to_yaml($dns_reverse_zones),
    }

    # Parse K8S cluster info and create new hash with relevant data
    $k8s_delegation_data = $kubernetes_clusters.reduce({}) |$accumulated, $cluster_info| {
        $cluster_info[1].reduce($accumulated) |$sub_accumulated, $sub_clusters| {
            $sub_accumulated + {
                $sub_clusters[0] => {
                    'networks'     => $sub_clusters[1]['cluster_cidr'].values,
                    'name_servers' => $sub_clusters[1]['control_plane_nodes']
                }
            }
        }
    }
    # Write this data to file the generation script uses
    file { '/etc/netbox/dns_k8s_reverse_delegation.yaml':
        owner   => 'netbox',
        group   => 'www-data',
        mode    => '0440',
        content => to_yaml($k8s_delegation_data)
    }
}
