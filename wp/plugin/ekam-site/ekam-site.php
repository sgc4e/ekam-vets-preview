<?php
/**
 * Plugin Name: ekam vets site
 * Description: What build.py did for the static site: old .html URLs redirect, Open Graph, clinic JSON-LD, sitemap rules. Lives in a plugin so it survives a theme change.
 * Version: 1.0.0
 */

defined( 'ABSPATH' ) || exit;

/*
 * 1. Old static URLs -> WordPress URLs, 301.
 *    /index.html -> /      /rates.html -> /rates/      /hi/rates.html -> /hi/rates/
 *    /sitemap.xml -> /wp-sitemap.xml
 * send.php still redirects to /thanks.html and /visit.html?e=1, so these rules also
 * make the booking form work without editing send.php.
 */
add_action( 'template_redirect', function () {
	$uri  = $_SERVER['REQUEST_URI'] ?? '';
	$path = (string) wp_parse_url( $uri, PHP_URL_PATH );
	$qs   = (string) wp_parse_url( $uri, PHP_URL_QUERY );
	$base = untrailingslashit( (string) wp_parse_url( home_url( '/' ), PHP_URL_PATH ) );
	if ( $base && str_starts_with( $path, $base . '/' ) ) {
		$path = substr( $path, strlen( $base ) );
	}

	if ( '/sitemap.xml' === $path ) {
		wp_safe_redirect( home_url( '/wp-sitemap.xml' ), 301 );
		exit;
	}
	if ( ! preg_match( '#^/(hi/)?([a-z0-9-]+)\.html$#', $path, $m ) ) {
		return;
	}
	$slug = 'index' === $m[2] ? '' : $m[2] . '/';
	$to   = home_url( '/' . $m[1] . $slug ) . ( $qs ? '?' . $qs : '' );
	wp_safe_redirect( $to, 301 );
	exit;
}, 0 );

// WordPress would otherwise try to "guess" a 404 into the nearest slug before our rule runs.
add_filter( 'redirect_canonical', function ( $to, $from ) {
	return preg_match( '#\.html(\?|$)#', (string) $from ) ? false : $to;
}, 10, 2 );

/*
 * 2. Open Graph, as build.py wrote it. og:locale follows the page language.
 */
add_action( 'wp_head', function () {
	if ( ! ( is_singular() || is_front_page() || is_home() ) ) {
		return;
	}
	$id    = is_home() ? (int) get_option( 'page_for_posts' ) : get_queried_object_id();
	$title = get_post_meta( $id, 'ekam_title', true ) ?: wp_get_document_title();
	$desc  = get_post_meta( $id, 'ekam_description', true );
	$url   = is_front_page() ? home_url( '/' ) : get_permalink( $id );
	$hi    = str_starts_with( get_locale(), 'hi' ) || ( function_exists( 'pll_get_post_language' ) && 'hi' === pll_get_post_language( $id ) );
	$tags  = array(
		'og:type'        => is_singular( 'post' ) ? 'article' : 'website',
		'og:site_name'   => 'ekam vets',
		'og:title'       => $title,
		'og:description' => $desc,
		'og:url'         => $url,
		'og:image'       => ekam_logo_url(),
		'og:locale'      => $hi ? 'hi_IN' : 'en_IN',
	);
	foreach ( array_filter( $tags ) as $p => $c ) {
		printf( '<meta property="%s" content="%s">' . "\n", esc_attr( $p ), esc_attr( $c ) );
	}
	if ( is_front_page() ) {
		echo ekam_schema(); // phpcs:ignore WordPress.Security.EscapeOutput -- built from constants and wp_json_encode.
	}
}, 5 );

function ekam_logo_url() {
	$theme = get_theme_file_path( 'assets/img/logo.png' );
	return file_exists( $theme ) ? get_theme_file_uri( 'assets/img/logo.png' ) : '';
}

/*
 * 3. VeterinaryCare JSON-LD on the home page. Same facts as build.py.
 *    No priceRange: SG, 18 Oct 2026, no prices anywhere on the site.
 */
function ekam_schema() {
	$logo = ekam_logo_url();
	$data = array(
		'@context'                  => 'https://schema.org',
		'@type'                     => 'VeterinaryCare',
		'name'                      => 'ekam vets',
		'description'               => 'Integrated holistic veterinary clinic in Vidyadhar Nagar, Jaipur. Medicine, physiotherapy, homeopathy, herbal medicine, in-house lab, operation theatre and in-patient beds under one roof.',
		'url'                       => home_url( '/' ),
		'logo'                      => $logo,
		'image'                     => $logo,
		'telephone'                 => '+919165931975',
		'currenciesAccepted'        => 'INR',
		'paymentAccepted'           => 'Cash, UPI, Card',
		'address'                   => array(
			'@type'           => 'PostalAddress',
			'streetAddress'   => '134, Sector 1, Vidyadhar Nagar',
			'addressLocality' => 'Jaipur',
			'addressRegion'   => 'Rajasthan',
			'postalCode'      => '302039',
			'addressCountry'  => 'IN',
		),
		'areaServed'                => array_map(
			fn( $n ) => array( '@type' => 'Place', 'name' => $n ),
			array( 'Vidyadhar Nagar', 'Shastri Nagar', 'Jhotwara', 'Jaipur' )
		),
		'openingHoursSpecification' => array(
			array( '@type' => 'OpeningHoursSpecification', 'dayOfWeek' => array( 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ), 'opens' => '09:00', 'closes' => '20:00' ),
			array( '@type' => 'OpeningHoursSpecification', 'dayOfWeek' => 'Sunday', 'opens' => '10:00', 'closes' => '14:00' ),
		),
		'availableService'          => array_map(
			fn( $n ) => array( '@type' => 'MedicalProcedure', 'name' => $n ),
			array(
				'Veterinary consultation',
				'Animal physiotherapy',
				'Homeopathy prescribed by a registered veterinary surgeon',
				'Herbal and natural medicine',
				'Massage and acupuncture',
				'Senior and palliative care',
				'In-house laboratory and imaging',
				'Surgery and in-patient care',
				'Grooming',
			)
		),
	);
	return '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . "</script>\n";
}

/*
 * 4. Sitemap: pages and posts only, thanks pages out (they are noindex), no author archives.
 */
add_filter( 'wp_sitemaps_add_provider', fn( $provider, $name ) => 'users' === $name ? false : $provider, 10, 2 );
add_filter( 'wp_sitemaps_taxonomies', fn() => array() );
add_filter( 'wp_sitemaps_posts_query_args', function ( $args ) {
	$thanks = get_posts( array( 'name' => 'thanks', 'post_type' => 'page', 'fields' => 'ids', 'post_status' => 'any', 'numberposts' => -1, 'lang' => '' ) );
	$args['post__not_in'] = array_merge( $args['post__not_in'] ?? array(), $thanks );
	return $args;
} );

// No author archives at all: the site names no people.
add_action( 'template_redirect', function () {
	if ( is_author() ) {
		wp_safe_redirect( home_url( '/' ), 301 );
		exit;
	}
} );

/*
 * 5. Subfolder installs (staging at ekamvets.com/staging/). Content, header, footer and tab bar
 *    link root-relative ("/visit/"). Prefix them with the install path so they stay inside the
 *    install. On ekamvets.com the path is "/" and this does nothing.
 *    Left alone: /hi/ (the static Hindi site stays at the domain root), /wp-* paths, and
 *    links already carrying the prefix.
 */
add_filter( 'render_block', function ( $html ) {
	$base = untrailingslashit( (string) wp_parse_url( home_url( '/' ), PHP_URL_PATH ) );
	if ( '' === $base ) {
		return $html;
	}
	$q = preg_quote( $base, '#' );
	return preg_replace( '#href="/(?!/|hi/|wp-|' . ltrim( $q, '/' ) . '/)#', 'href="' . $base . '/', $html );
}, 5 );
