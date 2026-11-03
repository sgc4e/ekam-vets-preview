<?php
/**
 * ekam vets block theme.
 */

const EKAM_FONTS = 'https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:ital,wght@0,400;0,500;0,700;1,400;1,500&family=Mukta:wght@300;400;600;700&display=swap';

// Fonts load on the front end and inside the editor iframe.
add_action( 'enqueue_block_assets', function () {
	wp_enqueue_style( 'ekam-fonts', EKAM_FONTS, array(), null );
} );

add_action( 'wp_enqueue_scripts', function () {
	// Version = file mtime, so browsers never keep a stale stylesheet after an edit.
	$v = fn( $f ) => (string) filemtime( get_theme_file_path( $f ) );
	wp_enqueue_style( 'ekam-site', get_theme_file_uri( 'assets/site.css' ), array(), $v( 'assets/site.css' ) );
	wp_enqueue_style( 'ekam-compat', get_theme_file_uri( 'assets/wp-compat.css' ), array( 'ekam-site' ), $v( 'assets/wp-compat.css' ) );
} );

add_action( 'wp_head', function () {
	echo '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
	if ( ! has_site_icon() ) {
		printf( '<link rel="icon" type="image/png" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/img/favicon.png' ) ) );
	}
	$desc = is_singular() || is_home() ? get_post_meta( get_queried_object_id(), 'ekam_description', true ) : '';
	if ( $desc ) {
		printf( '<meta name="description" content="%s">' . "\n", esc_attr( $desc ) );
	}
}, 1 );

// <title> and meta description carried over from the static pages (set by import.php).
add_filter( 'pre_get_document_title', function ( $title ) {
	return ( is_singular() || is_home() ) && ( $t = get_post_meta( get_queried_object_id(), 'ekam_title', true ) ) ? $t : $title;
} );

// Keep copy exactly as written (no smart quotes, no 24x7 -> 24×7).
add_filter( 'run_wptexturize', '__return_false' );

add_action( 'after_setup_theme', function () {
	add_theme_support( 'editor-styles' );
	add_editor_style( array( 'assets/site.css', 'assets/wp-compat.css' ) );
} );

// .btn variants from the static site, picked from the Styles panel of a Button block.
add_action( 'init', function () {
	foreach ( array( 'dark' => 'Dark', 'line' => 'Line', 'ghost' => 'Ghost' ) as $name => $label ) {
		register_block_style( 'core/button', array( 'name' => $name, 'label' => $label ) );
	}
} );

// Only administrators may lock or unlock blocks (the homeopathy and pricing paragraphs are locked).
add_filter( 'block_editor_settings_all', function ( $settings ) {
	$settings['canLockBlocks'] = current_user_can( 'manage_options' );
	return $settings;
} );

// The thanks page stays out of search, as on the static site.
add_filter( 'wp_robots', function ( $robots ) {
	return is_page( 'thanks' ) ? array_merge( $robots, array( 'noindex' => true, 'nofollow' => true ) ) : $robots;
} );

add_filter( 'render_block', function ( $html, $block ) {
	// Brand is lower case, always.
	$html = str_replace( array( 'Ekam Vets', 'Ekam vets' ), 'ekam vets', $html );

	// Blog stays highlighted in the header on a single post.
	if ( 'core/navigation-link' === $block['blockName'] && is_singular( 'post' )
		&& (int) ( $block['attrs']['id'] ?? 0 ) === (int) get_option( 'page_for_posts' ) ) {
		$html = preg_replace( '/class="wp-block-navigation-item /', 'class="wp-block-navigation-item current-menu-item ', $html, 1 );
	}

	// Mobile tab bar: mark the tab for the current URL.
	if ( 'core/html' === $block['blockName'] && str_contains( $html, 'class="tabbar"' ) ) {
		$path = wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH );
		$html = str_replace( 'href="' . esc_attr( $path ) . '"', 'href="' . esc_attr( $path ) . '" class="on"', $html );
	}
	return $html;
}, 10, 2 );
