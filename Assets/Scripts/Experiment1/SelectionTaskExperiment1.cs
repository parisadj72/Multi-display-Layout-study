using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SelectionTaskExperiment1 : MonoBehaviour
{
    public int numberOfTrials = 5;
    public int numberOfRepeatPerLayout = 3;
    private List<int> generateUniqueRandoms(int size, int repeat)
    {
        List<int> list = new List<int>(new int[size * repeat]);
        List<int> countList = new List<int>(new int[size]);

        for (int j = 0; j < size * repeat; j++)
        {
            int Rand = Random.Range(0, size);

            while (list.Contains(Rand) && countList[Rand] >= repeat)
            {
                Rand = Random.Range(0, size);
            }

            list[j] = Rand;
            countList[Rand]++;
        }
        return list;
    }

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(waiter());
    }
    IEnumerator waiter()
    {
        List<int> list = generateUniqueRandoms(gameObject.transform.childCount, numberOfRepeatPerLayout);

        for (int i = 0; i < list.Count; i++)
        {
            GameObject layout = gameObject.transform.GetChild(list[i]).gameObject;
            layout.transform.position = new Vector3(0.0f, 0.8f, 0.0f);
            layout.SetActive(true);

            List<ViewScript> views = new List<ViewScript>();
            Transform[] ViewsTransforms = layout.GetComponentsInChildren<Transform>();
            foreach (Transform childTransform in ViewsTransforms)
            {
                ViewScript view = childTransform.GetComponent<ViewScript>();

                if (view != null)
                {
                    view.TurnOff();
                    view.DisableInteraction();
                    views.Add(view);
                }
            }
            int numberOfWindows = views.Count;

            List<int> randomOrder = generateUniqueRandoms(numberOfWindows, numberOfTrials); // random order
            
            for (int j = 0; j < numberOfTrials; j++) // turn on one random view and enable interaction
            {
                views[randomOrder[j]].TurnOn();
                views[randomOrder[j]].EnableInteraction();
                yield return new WaitUntil(() => !views[randomOrder[j]].IsOn);

                // turn off the view and disable interaction
                views[randomOrder[j]].TurnOff();
                views[randomOrder[j]].DisableInteraction();
            }

            yield return new WaitForSeconds(5);
            layout.SetActive(false);

        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
