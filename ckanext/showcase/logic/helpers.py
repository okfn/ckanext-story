import re
import logging
import ckan.lib.helpers as h
from ckan import model
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


def get_groups_for_form(selected_groups=[]):
    context = {'model': model}

    # Get groups
    groups = tk.get_action('group_list')(context, {
        'sort': 'title asc',
        'type': config.get('ckanext.showcase.group_type', 'group'),
        'all_fields': True,
    })

    # Mark selected
    selected_names = map(lambda group: group['name'], selected_groups)
    for group in groups:
        if group['name'] in selected_names:
            group['selected'] = 'selected'

    return groups


def get_related_datasets_for_form(selected_ids=[], exclude_ids=[], topic_name=None):
    context = {'model': model}

    # Get packages
    limit = 1000  # ckan hard-limit
    page = 1
    packages = []
    while True:
        query = {
            'fq': 'dataset_type:dataset',
            'include_private': False,
            'sort': 'organization asc, title asc',
            'rows': limit,
            'start': limit * (page - 1),
        }
        if topic_name:
            query['q'] = 'groups:%s' % topic_name
        response = tk.get_action('package_search')(context, query)
        results = response.get('results', [])
        if len(results):
            packages.extend(results)
            page = page + 1
        else:
            break

    # Get orgs
    orgs = []
    current_org = None
    selected_ids = selected_ids if isinstance(selected_ids, list) else selected_ids.strip('{}').split(',')
    for package in packages:
        if package['id'] in exclude_ids:
            continue
        if package['owner_org'] != current_org:
            current_org = package['owner_org']
            orgs.append({'text': package['organization']['title'], 'children': []})
        dataset = {'text': package['title'], 'value': package['id']}
        if package['id'] in selected_ids:
            dataset['selected'] = 'selected'
        orgs[-1]['children'].append(dataset)

    return orgs


def get_related_stories_for_form(selected_ids=[], exclude_ids=[], topic_name=None):
    context = {'model': model}

    # Get packages
    limit = 1000  # ckan hard-limit
    page = 1
    packages = []
    while True:
        query = {
            'fq': 'dataset_type:showcase',
            'include_private': False,
            'sort': 'organization asc, title asc',
            'rows': limit,
            'start': limit * (page - 1),
        }
        if topic_name:
            query['q'] = 'groups:%s' % topic_name
        response = tk.get_action('package_search')(context, query)
        results = response.get('results', [])
        if len(results):
            packages.extend(results)
            page = page + 1
        else:
            break

    # Get datasets
    datasets = []
    selected_ids = selected_ids if isinstance(selected_ids, list) else selected_ids.strip('{}').split(',')
    for package in packages:
        dataset = {'text': package['title'], 'value': package['id']}
        if package['id'] in exclude_ids:
            continue
        if package['id'] in selected_ids:
            dataset['selected'] = 'selected'
        datasets.append(dataset)

    return datasets


def get_related_datasets_for_display(value):
    context = {'model': model}

    # Get datasets
    datasets = []
    ids = value if isinstance(value, list) else value.strip('{}').split(',')
    for id in ids:
        try:
            dataset = tk.get_action('package_show')(context, {'id': id})
            href = tk.url_for('dataset_read', id=dataset['name'], qualified=False)
            datasets.append({'text': dataset['title'], 'href': href})
        except tk.ObjectNotFound:
            pass

    return datasets


def get_related_stories_for_display(value):
    context = {'model': model}

    # Get datasets
    datasets = []
    ids = value if isinstance(value, list) else value.strip('{}').split(',')
    for id in ids:
        try:
            dataset = tk.get_action('package_show')(context, {'id': id})
            href = tk.url_for('ckanext_showcase_read', id=dataset['name'], qualified=False)
            datasets.append({'text': dataset['title'], 'href': href})
        except tk.ObjectNotFound:
            pass

    return datasets


def get_methodologies_for_form():
    stories = tk.get_action('package_search')({'model': model}, {
        'q': 'story_type:Methodologies',
        'fq': 'dataset_type:showcase',
        'include_private': False,
        'sort': 'organization asc, title asc',
    })['results']
    return [{'value': ''}] + [{'text': story['title'], 'value': story['id']} for story in stories]


def get_author_profiles_for_form():
    stories = tk.get_action('package_search')({'model': model}, {
        'q': 'story_type:"Author Profiles"',
        'fq': 'dataset_type:showcase',
        'include_private': False,
        'sort': 'organization asc, title asc',
    })['results']
    return [{'value': ''}] + [{'text': story['title'], 'value': story['id']} for story in stories]
