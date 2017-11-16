import argparse, json
import simpleamt

if __name__ == '__main__':
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--prod', action='store_false', dest='sandbox',
                      default=True,
                      help="Whether to run on the production AMT site.")
  parser.add_argument('--assignment_ids_file')
  parser.add_argument('-f', action='store_true', default=False)
  parser.add_argument('--config', default='config.json', type=simpleamt.json_file)
  args = parser.parse_args()
  mtc = simpleamt.get_mturk_connection_from_args(args)

  approve_ids = []
  reject_ids = []

  if args.assignment_ids_file is None:
    parser.error('Must specify --assignment_ids_file.')

  with open(args.assignment_ids_file, 'r') as f:
    assignment_ids = [line.strip() for line in f]

  for a_id in assignment_ids:
    a = mtc.get_assignment(a_id)[0]
    if a.AssignmentStatus == 'Submitted':
      try:
        # Try to parse the output from the assignment. If it isn't
        # valid JSON then we reject the assignment.
        output = json.loads(a.answers[0][0].fields[0])
        approve_ids.append(a_id)
      except ValueError as e:
        reject_ids.append(a_id)

  print(('This will approve %d assignments and reject %d assignments with '
         'sandbox=%s' % (len(approve_ids), len(reject_ids), str(args.sandbox))))
  print('Continue?')

  if not args.f:
    s = input('(Y/N): ')
  else:
    s = 'Y'
  if s == 'Y' or s == 'y':
    print('Approving assignments')
    for idx, assignment_id in enumerate(approve_ids):
      print('Approving assignment %d / %d' % (idx + 1, len(approve_ids)))
      mtc.approve_assignment(assignment_id)
    for idx, assignment_id in enumerate(reject_ids):
      print('Rejecting assignment %d / %d' % (idx + 1, len(reject_ids)))
      mtc.reject_assignment(assignment_id, feedback='Invalid results')
  else:
    print('Aborting')
