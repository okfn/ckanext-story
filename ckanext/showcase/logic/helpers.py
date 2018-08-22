import re
import logging
import ckan.lib.helpers as h
from ckan.common import config
from ckan.plugins import toolkit as tk
log = logging.getLogger(__name__)


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.showcase.controller:ShowcaseController',
        action='search')


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': 'dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats


def is_disqus_enabled():
    return bool(config.get('disqus.name'))


def search_emdedded_elements(text):
    elements = []

    # Datasets
    PATTERN = r'%s/dataset/([\w-]+)/resource/([\w-]+)/view/([\w-]+)'
    matches = re.findall(PATTERN % re.escape(tk.config.get('ckan.site_url')), text)
    for match in matches:
        elements.append({
            'type': 'dataset',
            'dataset': match[0],
            'resource': match[1],
            'view': match[2],
        })

    return elements


def get_related_datasets_for_form(type='dataset', selected_ids=[], exclude_ids=[]):
    context = {'model': model}

    # Get search results
    search_datasets = toolkit.get_action('package_search')
    search = search_datasets(context, {
        'fq': 'dataset_type:%s' % type,
        'include_private': False,
        'sort': 'organization asc, title asc',
    })

    # Get datasets
    orgs = []
    current_org = None
    selected_ids = selected_ids if isinstance(selected_ids, list) else selected_ids.strip('{}').split(',')
    for package in search['results']:
        dataset = {'text': package['title'], 'value': package['id']}

        # Skip excluded
        if package['id'] in exclude_ids:
            continue

        # Mark selected
        if package['id'] in selected_ids:
            dataset['selected'] = 'selected'

        # Handle hierarchy
        if package['owner_org'] != current_org:
            current_org = package['owner_org']
            orgs.append({'text': package['organization']['title'], 'children': []})
        orgs[-1]['children'].append(dataset)

    return orgs


def get_related_datasets_for_display(value):
    context = {'model': model}

    # Get datasets
    datasets = []
    ids = value if isinstance(value, list) else value.strip('{}').split(',')
    for id in ids:
        dataset = toolkit.get_action('package_show')(context, {'id': id})
        href = toolkit.url_for('dataset_read', id=dataset['name'], qualified=True)
        datasets.append({'text': dataset['title'], 'href': href})

    return datasets
