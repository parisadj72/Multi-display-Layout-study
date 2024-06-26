using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class MemoryTaskExperiment2 : MonoBehaviour
{
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
        List<int> list = generateUniqueRandoms(gameObject.transform.childCount, 3);

        for (int i = 0; i < list.Count; i++)
        {
            GameObject layout = gameObject.transform.GetChild(list[i]).gameObject;
            layout.transform.position = new Vector3(0.0f, 0.6f, 0.0f);
            layout.SetActive(true);

            List<ViewScript> views = new List<ViewScript>();            
            Transform[] ViewsTransforms = layout.GetComponentsInChildren<Transform>();
            foreach (Transform childTransform in ViewsTransforms)
            {
                ViewScript view = childTransform.GetComponent<ViewScript>();

                if (view != null)
                {
                    view.DisableInteraction();
                    views.Add(view);
                }
            }
            int numberOfWindows = views.Count;

            if (numberOfWindows == 3)
            {
                List<int> rand2 = generateUniqueRandoms(3, 1); // random order
                for (int j = 0; j < 2; j++) // turn on 2 random views
                    views[rand2[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 2; j++) // turn off the 2 views and enable interaction
                {
                    views[rand2[j]].TurnOff();
                    views[rand2[j]].EnableInteraction();
                }

                yield return new WaitUntil(() => views[rand2[0]].IsOn && views[rand2[1]].IsOn);
            }
            else if (numberOfWindows == 6)
            {
                List<int> rand3 = generateUniqueRandoms(6, 1);
                for (int j = 0; j < 3; j++) // turn on 3 random views
                    views[rand3[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 3; j++) // turn off the 3 views
                {
                    views[rand3[j]].TurnOff();
                    views[rand3[j]].EnableInteraction();
                }
                yield return new WaitUntil(() => views[rand3[0]].IsOn && views[rand3[1]].IsOn && views[rand3[2]].IsOn);
            }
            else // numberOfWindows == 12
            {
                List<int> rand5 = generateUniqueRandoms(12, 1);
                for (int j = 0; j < 5; j++) // turn on 5 random views
                    views[rand5[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 5; j++) // turn off the 5 views
                { 
                    views[rand5[j]].TurnOff();
                    views[rand5[j]].EnableInteraction();
                }
                yield return new WaitUntil(() => views[rand5[0]].IsOn && views[rand5[1]].IsOn && views[rand5[2]].IsOn && views[rand5[3]].IsOn && views[rand5[4]].IsOn);
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
