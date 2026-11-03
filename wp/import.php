<?php
/**
 * Import the converted ekam vets content into WordPress.
 *
 *   wp eval-file wp/import.php            (production, WP-CLI)
 *   require after wp-load.php             (Playground, see blueprint.json)
 *
 * Idempotent: pages and posts are matched by slug and updated in place, so it can be
 * re-run after every `python3 wp/convert.py`. Edits made in wp-admin to imported
 * pages are overwritten by a re-run.
 *
 * English only for now. Hindi (content/hi) is converted but not imported: once the
 * translation plugin is chosen, add 'hi' to EKAM_LANGS and link each Hindi post to its
 * English original inside ekam_after_upsert(), using the plugin's API.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit( "Run inside WordPress: wp eval-file import.php\n" );
}

const EKAM_LANGS = array( 'en' );
const EKAM_POST_DATE = '2026-08-29 12:00:00'; // newest card on blog.html gets this date, the rest one day apart
$ekam_dir = __DIR__;

function ekam_log( $msg ) {
	class_exists( 'WP_CLI' ) ? WP_CLI::log( $msg ) : print( $msg . "\n" );
}

// Act as an administrator so kses keeps the booking form, SVG icons and class names.
if ( ! current_user_can( 'unfiltered_html' ) ) {
	$admins = get_users( array( 'role' => 'administrator', 'number' => 1, 'fields' => 'ID' ) );
	wp_set_current_user( (int) $admins[0] );
}
kses_remove_filters();

/** Attachment that points at a hotlinked Unsplash URL (no download), for featured images. */
function ekam_external_image( $url, $alt ) {
	$found = get_posts( array( 'post_type' => 'attachment', 'post_status' => 'inherit', 'meta_key' => '_ekam_src', 'meta_value' => $url, 'fields' => 'ids', 'numberposts' => 1 ) );
	if ( $found ) {
		return $found[0];
	}
	parse_str( (string) wp_parse_url( $url, PHP_URL_QUERY ), $q );
	$w  = (int) ( $q['w'] ?? 900 );
	$h  = (int) ( $q['h'] ?? 560 );
	$id = wp_insert_attachment( array( 'guid' => $url, 'post_mime_type' => 'image/jpeg', 'post_title' => $alt, 'post_status' => 'inherit' ) );
	update_post_meta( $id, '_ekam_src', $url );
	update_post_meta( $id, '_wp_attachment_image_alt', $alt );
	// No _wp_attached_file: wp_get_attachment_url() then falls back to the guid, i.e. the Unsplash URL.
	wp_update_attachment_metadata( $id, array(
		'width'  => $w,
		'height' => $h,
		'sizes'  => array( 'full' => array( 'file' => wp_basename( $url ), 'width' => $w, 'height' => $h, 'mime-type' => 'image/jpeg' ) ),
	) );
	return $id;
}

/** Copy a theme image into the media library once (used for the site logo). */
function ekam_theme_image( $file ) {
	$found = get_posts( array( 'post_type' => 'attachment', 'post_status' => 'inherit', 'meta_key' => '_ekam_src', 'meta_value' => "theme:$file", 'fields' => 'ids', 'numberposts' => 1 ) );
	if ( $found ) {
		return $found[0];
	}
	require_once ABSPATH . 'wp-admin/includes/image.php';
	$up = wp_upload_bits( basename( $file ), null, file_get_contents( get_theme_root() . "/ekam-vets/assets/img/$file" ) );
	$id = wp_insert_attachment( array( 'post_mime_type' => 'image/png', 'post_title' => 'ekam vets', 'post_status' => 'inherit' ), $up['file'] );
	wp_update_attachment_metadata( $id, wp_generate_attachment_metadata( $id, $up['file'] ) );
	update_post_meta( $id, '_ekam_src', "theme:$file" );
	update_post_meta( $id, '_wp_attachment_image_alt', 'ekam vets' );
	return $id;
}

function ekam_category( $name ) {
	$term = term_exists( $name, 'category' ) ?: wp_insert_term( $name, 'category' );
	return (int) $term['term_id'];
}

function ekam_upsert( array $e, $lang, $dir ) {
	$slug    = 'index' === $e['slug'] ? 'home' : $e['slug'];
	$content = file_get_contents( "$dir/content/$lang/{$e['slug']}.html" );
	// Root-relative, so the same content works on staging and on ekamvets.com without a search-replace.
	$content = str_replace( '{{theme}}', wp_make_link_relative( content_url( 'themes/ekam-vets' ) ), $content );
	$found   = get_page_by_path( $slug, OBJECT, $e['type'] );

	$post = array(
		'ID'           => $found ? $found->ID : 0,
		'post_type'    => $e['type'],
		'post_status'  => 'publish',
		'post_name'    => $slug,
		'post_title'   => $e['title'],
		'post_content' => $content,
		'post_excerpt' => $e['excerpt'] ?? '',
		'meta_input'   => array( 'ekam_title' => $e['document_title'], 'ekam_description' => $e['description'] ),
	);
	if ( 'post' === $e['type'] ) {
		$post['post_date']     = gmdate( 'Y-m-d H:i:s', strtotime( EKAM_POST_DATE ) - $e['order'] * DAY_IN_SECONDS );
		$post['post_category'] = array( ekam_category( $e['category'] ) );
	}
	$id = wp_insert_post( wp_slash( $post ), true );
	if ( is_wp_error( $id ) ) {
		ekam_log( "  FAILED {$e['slug']}: " . $id->get_error_message() );
		return 0;
	}
	if ( 'post' === $e['type'] ) {
		set_post_thumbnail( $id, ekam_external_image( $e['image']['url'], $e['image']['alt'] ) );
	}
	ekam_after_upsert( $id, $e, $lang );
	ekam_log( sprintf( '  %s %s %-28s #%d', $found ? 'updated' : 'created', $e['type'], $slug, $id ) );
	return $id;
}

/** Hook for the translation plugin: set the post language and link it to the English original. */
function ekam_after_upsert( $id, array $e, $lang ) {
}

$manifest = json_decode( file_get_contents( "$ekam_dir/content/manifest.json" ), true );
$ids      = array();
foreach ( EKAM_LANGS as $lang ) {
	ekam_log( "Importing $lang" );
	foreach ( $manifest[ $lang ] as $e ) {
		$ids[ $lang ][ $e['slug'] ] = ekam_upsert( $e, $lang, $ekam_dir );
	}
}
$en = $ids['en'];

// Site identity. The brand is lower case.
update_option( 'blogname', 'ekam vets' );
update_option( 'blogdescription', 'Integrated holistic vets' );
update_option( 'site_logo', ekam_theme_image( 'logo-mark-t.png' ) );

// Static front page and posts page.
update_option( 'show_on_front', 'page' );
update_option( 'page_on_front', $en['index'] );
update_option( 'page_for_posts', $en['blog'] );

// Pretty permalinks: /rates/, /blog-heat-stroke/.
global $wp_rewrite;
$wp_rewrite->set_permalink_structure( '/%postname%/' );
flush_rewrite_rules( true );

// Header menu (wp_navigation). The header part's Navigation block has no ref, so WordPress
// uses the most recently published menu: post_date is bumped to now on every run.
$link = function ( $label, $slug, $class = '' ) use ( $en ) {
	$attrs = array( 'label' => $label, 'type' => 'page', 'id' => $en[ $slug ], 'url' => wp_make_link_relative( get_permalink( $en[ $slug ] ) ), 'kind' => 'post-type' );
	if ( $class ) {
		$attrs['className'] = $class;
	}
	return array( 'blockName' => 'core/navigation-link', 'attrs' => $attrs, 'innerBlocks' => array(), 'innerHTML' => '', 'innerContent' => array() );
};
$items = array(
	$link( 'Home', 'index' ),
	$link( 'Integrated care', 'integrated-care' ),
	$link( 'Services', 'services' ),
	$link( 'Rate card', 'rates' ),
	$link( 'About', 'about' ),
	$link( 'Blog', 'blog' ),
	// LANGUAGE SWITCHER PLACEHOLDER: replace this item with the Hindi plugin's switcher.
	array( 'blockName' => 'core/navigation-link', 'attrs' => array( 'label' => 'हिंदी', 'url' => '/hi/', 'kind' => 'custom', 'className' => 'lang lang-switcher-placeholder' ), 'innerBlocks' => array(), 'innerHTML' => '', 'innerContent' => array() ),
	$link( 'Book Now', 'visit', 'cta' ),
);
$nav = get_posts( array( 'post_type' => 'wp_navigation', 'name' => 'header-navigation', 'post_status' => 'any', 'numberposts' => 1 ) );
wp_insert_post( wp_slash( array(
	'ID'           => $nav ? $nav[0]->ID : 0,
	'post_type'    => 'wp_navigation',
	'post_status'  => 'publish',
	'post_name'    => 'header-navigation',
	'post_title'   => 'Header',
	'post_date'    => current_time( 'mysql' ),
	'post_content' => serialize_blocks( $items ),
) ) );

ekam_log( sprintf( 'Done: %d pages/posts, front page #%d, posts page #%d.', count( $en ), $en['index'], $en['blog'] ) );
