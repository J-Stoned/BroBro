/**
 * Funnel Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Provides MCP tools for managing GoHighLevel funnels including:
 * - Listing all funnels in a location
 * - Getting pages for a specific funnel
 * - Creating new funnels with pages
 *
 * GHL Funnels Documentation:
 * - Funnels are collections of pages (landing, sales, thank-you, etc.)
 * - Each funnel has: name, domain, pages, status
 * - API Endpoints: /funnels, /funnels/{funnelId}/pages
 */

import { z } from 'zod';
import { ghlClient } from '../api/ghl-client.js';
import { logger } from '../utils/logger.js';

/**
 * List Funnels Tool
 *
 * Lists all funnels in a GoHighLevel location with filtering options.
 */
export const listFunnelsTool = {
  name: 'list_funnels',
  description: 'List all funnels in a GoHighLevel location. Funnels are collections of pages for marketing campaigns, sales processes, and lead generation.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID to list funnels from'),
    category: z.enum(['all', 'sales', 'lead_gen', 'webinar', 'membership']).optional().default('all').describe('Filter by funnel category'),
    status: z.enum(['all', 'published', 'draft']).optional().default('all').describe('Filter by funnel status'),
    limit: z.number().optional().default(100).describe('Maximum number of funnels to return (default: 100)'),
    skip: z.number().optional().default(0).describe('Number of funnels to skip for pagination (default: 0)')
  }),

  async handler(args: {
    locationId: string;
    category?: 'all' | 'sales' | 'lead_gen' | 'webinar' | 'membership';
    status?: 'all' | 'published' | 'draft';
    limit?: number;
    skip?: number;
  }): Promise<string> {
    logger.info('list_funnels tool invoked', {
      locationId: args.locationId,
      category: args.category,
      status: args.status
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        locationId: args.locationId,
        limit: args.limit || 100,
        skip: args.skip || 0
      };

      // Add status filter if not 'all'
      if (args.status && args.status !== 'all') {
        params.status = args.status;
      }

      // Add category filter if not 'all'
      if (args.category && args.category !== 'all') {
        params.category = args.category;
      }

      // Get funnels from GHL API
      const result = await ghlClient.get('/funnels/', params);

      const funnels = result.funnels || [];

      logger.info('Funnels retrieved successfully', {
        count: funnels.length,
        locationId: args.locationId
      });

      // Format funnels for better readability
      const formattedFunnels = funnels.map((funnel: any) => ({
        id: funnel.id,
        name: funnel.name,
        category: funnel.category || 'uncategorized',
        status: funnel.status || 'draft',
        domain: funnel.domain || funnel.customDomain,
        pageCount: funnel.pages?.length || funnel.pageCount || 0,
        url: funnel.url || `https://${funnel.domain}`,
        createdAt: funnel.createdAt,
        updatedAt: funnel.updatedAt
      }));

      const response = {
        success: true,
        total: funnels.length,
        funnels: formattedFunnels,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: funnels.length === (args.limit || 100)
        },
        filters: {
          category: args.category,
          status: args.status
        },
        summary: {
          published: formattedFunnels.filter((f: any) => f.status === 'published').length,
          draft: formattedFunnels.filter((f: any) => f.status === 'draft').length,
          byCategory: formattedFunnels.reduce((acc: any, f: any) => {
            acc[f.category] = (acc[f.category] || 0) + 1;
            return acc;
          }, {})
        },
        nextSteps: [
          'Use get_funnel_pages to view pages in a specific funnel',
          'Use create_funnel to create a new funnel',
          'Access funnel URLs directly to view published pages',
          'To get more results, increase skip parameter'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to list funnels', {
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has funnel read permissions',
          'Ensure location has funnels created',
          'Try without filters if no results found'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Get Funnel Pages Tool
 *
 * Retrieves all pages for a specific funnel including URLs, types, and settings.
 */
export const getFunnelPagesTool = {
  name: 'get_funnel_pages',
  description: 'Get all pages for a specific funnel including URLs, page types, and configuration. Use this to understand funnel structure and access individual pages.',
  schema: z.object({
    funnelId: z.string().describe('The funnel ID to get pages from'),
    includeContent: z.boolean().optional().default(false).describe('Include page HTML content (can be large)')
  }),

  async handler(args: {
    funnelId: string;
    includeContent?: boolean;
  }): Promise<string> {
    logger.info('get_funnel_pages tool invoked', {
      funnelId: args.funnelId,
      includeContent: args.includeContent
    });

    try {
      // Get funnel details first to get funnel info
      const funnel = await ghlClient.get(`/funnels/${args.funnelId}`);

      // Get pages for the funnel
      const pagesResult = await ghlClient.get(`/funnels/${args.funnelId}/pages`);

      const pages = pagesResult.pages || pagesResult || [];

      logger.info('Funnel pages retrieved successfully', {
        funnelId: args.funnelId,
        pageCount: pages.length
      });

      // Format pages for better readability
      const formattedPages = pages.map((page: any, index: number) => {
        const pageInfo: any = {
          id: page.id,
          name: page.name,
          path: page.path || page.slug,
          url: page.url || `${funnel.url || funnel.domain}${page.path || page.slug}`,
          type: page.type || 'landing', // landing, thank-you, sales, checkout, etc.
          order: page.order !== undefined ? page.order : index,
          status: page.status || 'active',
          seoTitle: page.seoTitle || page.metaTitle,
          seoDescription: page.seoDescription || page.metaDescription,
          favicon: page.favicon,
          thumbnail: page.thumbnail,
          createdAt: page.createdAt,
          updatedAt: page.updatedAt
        };

        // Include content if requested (can be large)
        if (args.includeContent && page.content) {
          pageInfo.content = page.content;
        }

        return pageInfo;
      });

      const response = {
        success: true,
        funnel: {
          id: funnel.id,
          name: funnel.name,
          domain: funnel.domain || funnel.customDomain,
          url: funnel.url,
          status: funnel.status
        },
        pageCount: pages.length,
        pages: formattedPages,
        analysis: {
          pageTypes: formattedPages.reduce((acc: any, p: any) => {
            acc[p.type] = (acc[p.type] || 0) + 1;
            return acc;
          }, {}),
          activePages: formattedPages.filter((p: any) => p.status === 'active').length,
          hasSEO: formattedPages.filter((p: any) => p.seoTitle).length
        },
        nextSteps: [
          'Access page URLs directly to view published pages',
          'Use create_funnel to create a similar funnel structure',
          'Update page content through GHL interface',
          'Track page analytics in GHL dashboard'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to get funnel pages', {
        funnelId: args.funnelId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the funnel ID is correct',
          'Check OAuth token has funnel read permissions',
          'Ensure funnel exists and is not deleted',
          'Use list_funnels to find valid funnel IDs'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Create Funnel Tool
 *
 * Creates a new funnel in GoHighLevel with specified pages and configuration.
 */
export const createFunnelTool = {
  name: 'create_funnel',
  description: 'Create a new funnel in GoHighLevel with pages. Funnels are collections of marketing pages for lead generation, sales, webinars, etc.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID where the funnel will be created'),
    name: z.string().describe('Funnel name (e.g., "Lead Magnet Funnel", "Product Sales Funnel")'),
    category: z.enum(['sales', 'lead_gen', 'webinar', 'membership', 'other']).optional().default('lead_gen').describe('Funnel category'),
    domain: z.string().optional().describe('Custom domain for funnel (e.g., "funnel.yourdomain.com"). If not provided, uses GHL subdomain'),
    pages: z.array(z.object({
      name: z.string().describe('Page name'),
      path: z.string().describe('URL path (e.g., "/landing", "/thank-you")'),
      type: z.enum(['landing', 'thank-you', 'sales', 'checkout', 'webinar', 'other']).describe('Page type'),
      templateId: z.string().optional().describe('GHL template ID to use for page'),
      seoTitle: z.string().optional().describe('SEO page title'),
      seoDescription: z.string().optional().describe('SEO meta description')
    })).describe('Array of pages to create in funnel (at least 1 page required)'),
    status: z.enum(['published', 'draft']).optional().default('draft').describe('Initial funnel status (default: draft)')
  }).refine(data => data.pages.length > 0, {
    message: 'At least one page must be provided'
  }),

  async handler(args: {
    locationId: string;
    name: string;
    category?: 'sales' | 'lead_gen' | 'webinar' | 'membership' | 'other';
    domain?: string;
    pages: Array<{
      name: string;
      path: string;
      type: 'landing' | 'thank-you' | 'sales' | 'checkout' | 'webinar' | 'other';
      templateId?: string;
      seoTitle?: string;
      seoDescription?: string;
    }>;
    status?: 'published' | 'draft';
  }): Promise<string> {
    logger.info('create_funnel tool invoked', {
      locationId: args.locationId,
      name: args.name,
      pageCount: args.pages.length,
      category: args.category
    });

    try {
      // Build funnel payload
      const funnelData: Record<string, any> = {
        locationId: args.locationId,
        name: args.name,
        category: args.category || 'lead_gen',
        status: args.status || 'draft',
        pages: args.pages.map((page, index) => ({
          name: page.name,
          path: page.path.startsWith('/') ? page.path : `/${page.path}`,
          type: page.type,
          order: index,
          templateId: page.templateId,
          seoTitle: page.seoTitle || page.name,
          seoDescription: page.seoDescription || `${page.name} page`,
          status: 'active'
        }))
      };

      // Add custom domain if provided
      if (args.domain) {
        funnelData.customDomain = args.domain;
        funnelData.domain = args.domain;
      }

      // Create funnel via GHL API
      const result = await ghlClient.post('/funnels/', funnelData);

      const funnelId = result.funnel?.id || result.id;
      const funnelUrl = result.url || result.funnel?.url || (args.domain ? `https://${args.domain}` : 'TBD');

      logger.info('Funnel created successfully', {
        funnelId: funnelId,
        name: args.name,
        pageCount: args.pages.length
      });

      const response = {
        success: true,
        funnel: {
          id: funnelId,
          name: args.name,
          category: args.category,
          status: args.status || 'draft',
          domain: args.domain,
          url: funnelUrl,
          pageCount: args.pages.length
        },
        pages: args.pages.map((page) => ({
          name: page.name,
          path: page.path,
          type: page.type,
          url: `${funnelUrl}${page.path.startsWith('/') ? page.path : `/${page.path}`}`
        })),
        message: `Funnel "${args.name}" created successfully with ${args.pages.length} pages`,
        nextSteps: [
          'Use get_funnel_pages to view created pages',
          args.status === 'draft' ? 'Publish funnel when ready using GHL interface' : 'Funnel is published and live',
          'Customize page content in GHL page builder',
          'Set up tracking and analytics',
          'Test all funnel pages and flows',
          args.domain ? 'Configure DNS records for custom domain' : 'Consider adding custom domain for professional branding'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to create funnel', {
        name: args.name,
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has funnel creation permissions',
          'Ensure page paths are unique within the funnel',
          'Verify page paths start with "/" (e.g., "/landing")',
          'Check that domain is available if using custom domain',
          'Ensure template IDs are valid if provided',
          'Try creating with minimal pages first (1 landing page)'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};
