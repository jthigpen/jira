""" Jira Reporting Code """
import arrow


class CustomField:
    """ Encapsulates the Jira Custom Field properties """
    def __init__(self, field_id, name, field_name=None):
        self.field_id = field_id
        self.field_key = f"customfield_{field_id}"
        self.name = name
        if field_name != None:
            self.field_name = field_name
        else:
            self.field_name = name.lower().replace(" ", "_")

            
def retrieve_issues(jira_client):
    """ Runs a stupidly hard coded process to pull results doing a week based "pagination" """
    start = arrow.get("2021-03-01")
    # start = arrow.get("2022-03-01")
    end = arrow.utcnow()

    jql_template = """
    PROJECT = EN
    AND created >= {}
    AND created <= {}
    AND statusCategory = Done
    AND resolution = Done
    """

    result_list = []

    # If a result set has 99+ results, there's a good chance the API is limiting results and the date windows should be smaller.
    class LimitedResultsException(Exception):
        pass

    for r in arrow.Arrow.span_range('week', start, end):
        jql = jql_template.format(r[0].date(), r[1].date())
        print("Executing Search Query: {}".format(jql.replace("\n", " ").replace("\r", " ")))
        results = jira_client.search_issues(jql, expand="changelog,renderedFields")
        
        if len(results) >= 99:
            raise LimitedResultsException()
        result_list.extend(results)

    return result_list


class WorkflowTransitionDAO:
    """ Wrapper class to make the Jira history_item object easier to interact with """
    def __init__(self, timestamp, history_item):
        self._history_item = history_item
        
        self.field = history_item.field
        self.fieldtype = history_item.fieldtype
        
        self.timestamp = arrow.get(timestamp)
        
        self.from_state_id = getattr(history_item, "from")
        self.to_state_id = history_item.to
        
        self.from_state = history_item.fromString
        self.to_state = history_item.toString
        
    def __str__(self):
        return f"[{self.timestamp.date()}] '{self.from_state}'({self.from_state_id}) -> '{self.to_state}'({self.to_state_id})"


def try_parse_int(s, val=None):
    """ Convenient things are not /pythonic/ :vomit: """
    try:
        return int(s)
    except TypeError:
        return val

        
class Issue:
    """ Wrapper class for jira object because it's a pain in the butt to interact with """
    CUSTOM_FIELDS = []
    
    def __init__(self, issue):
        self._issue = issue
        self.key = issue.key
        self.project = issue.fields.project
        self.issuetype = issue.fields.issuetype.name
        self.assignee = issue.fields.assignee
        self.status = issue.fields.status
        self.summary = issue.fields.summary

        self.created_ts = issue.fields.created
        self.created_date = arrow.get(issue.fields.created).date()
        
        self.resolution_ts = issue.fields.resolutiondate
        self.resolution_date = arrow.get(issue.fields.resolutiondate).date()
        
        self._field_mappers = {
            "story_points": lambda x: try_parse_int(x),
            "team_assigned": lambda x: str(x.value) if x is not None else "Unassigned",
            "work_category": lambda x: str(x.value) if x is not None else "Uncategorized",
        }
        
        for cf in Issue.CUSTOM_FIELDS:
            if cf.field_name in self._field_mappers:
                mapper = self._field_mappers[cf.field_name]
            else:
                mapper = lambda x: x

            setattr(self, cf.field_name, mapper(getattr(self._issue.fields, cf.field_key, None)))
        
        
    @property
    def state_transitions(self):
        """ Return the workflow transitions for this ticket... maybe sorted by timestamp? Not sure. """
        history_items = WorkflowTransitionHistory()

        for h in self._issue.changelog.histories:
            for i in [x for x in h.items if x.field == 'status']:
                history_items.append(WorkflowTransitionDAO(h.created, i))
            # print(getattr(h, "created", None))
        
        return history_items
        
    def __str__(self):
        return f"[{self.key}]"
    
    def __repr__(self):
        return f"{self.key}"